# Editable Word diagrams (shapes + connectors) generated from Python, replacing PNG figures in the thesis DOCX pipeline

Scope note: the researcher tested this on this machine on 27/11/2026: Windows 11, Word 365 through COM, poppler 24.08. Proof-of-concept files are in the session scratchpad and are **not** in the repo:
`C:\Users\patph\AppData\Local\Temp\claude\85ae35366b529c68\b4942c2f-c1bf-4b4b-81ce-f0801cbaaca1\scratchpad\diagram_poc\`
- `make_poc.py`: builds a minimal DOCX with an inline `wpg` group and an inline `wpc` canvas.
- `inspect_shapes.ps1`, `check_word.ps1`, `export_report.ps1`: Word COM checks and PDF export.
- `inject_into_report.py`: injects a diagram into a **copy** of the built thesis DOCX.
- Renders: `poc-1.png`, `inj2-002.png`.

Below, "[PoC]" marks findings measured with these files.

## 1. How the existing pipeline inserts figures, and where a shape diagram fits

### Takeaway
Pandoc creates the figures as `<w:drawing><wp:inline>…pic:pic…</wp:inline></w:drawing>` inside a paragraph. `ooxml.restyle_paragraph` then restyles any paragraph that contains `<w:drawing>` to `FigurePara`, and the `@@CAP:fig@@` handler adds `keepNext` and a caption with `STYLEREF`+`SEQ Hình` fields. A shape diagram can enter through the same marker mechanism: a new `@@DIAGRAM:name@@` handler that returns a whole `<w:p>` with an inline `wpg`/`wpc` drawing. It needs no image relationship and no media file.

### Cited Findings
- Pandoc converts only the body to docx. The package is then assembled from the faculty template. Image relationships are rewritten to `rIdFig*` and the files are copied to `media/report_*` — [scripts/report_docx/package.py `assemble()` lines 366–425](../../scripts/report_docx/package.py)
- Paragraphs that contain `<w:drawing>` get style `FigurePara` — [scripts/report_docx/ooxml.py `restyle_paragraph` line 162](../../scripts/report_docx/ooxml.py)
- The `@@CAP:fig:key|…@@` marker adds `<w:keepNext/>` to the preceding `FigurePara` paragraph, then emits a Caption paragraph with `STYLEREF 1 \s` + `SEQ Hình \* ARABIC \s 1` fields and a bookmark for REF — [ooxml.py `transform_body` lines 289–298, `number_fields`, `caption_paragraph`](../../scripts/report_docx/ooxml.py)
- Other markers are dispatched to `handlers[name](argument)`. This is the natural hook for a `DIAGRAM` marker — [ooxml.py lines 299–304](../../scripts/report_docx/ooxml.py); [package.py `marker_handlers`](../../scripts/report_docx/package.py)
- `top_level_elements` already tracks nesting depth, so `<w:p>` elements nested inside `w:txbxContent` do not break the element split. Its docstring says "tính cả lồng trong text box" — [ooxml.py lines 43–60](../../scripts/report_docx/ooxml.py)
- The checker counts `<w:drawing>` occurrences ("Ảnh trong thân (gồm logo bìa)"). A group or canvas is one `<w:drawing>`, just like a picture, so the count does not change when a PNG is swapped for a diagram — [scripts/check_midterm_docx.py line 173](../../scripts/check_midterm_docx.py)
- The faculty template root (`report/Mau bao cao KLTN_DS.docx`) already declares `wpc`, `wpg`, `wps`, `wp`, `wp14`, `mc`, `v`, `o`, `w14`, with `mc:Ignorable="w14 w15 … wp14"`. The template itself contains `wps` connectors (cover lines) wrapped in `mc:AlternateContent` with VML fallback — [PoC inspection of template document.xml]
- **Pitfall:** the *final* Word-saved DOCX (`report/Khoa_luan_environmental_audio_rag.docx`) has **no `xmlns:a` on the root**, because Word declares `a` locally on each `<a:graphic>`. Injecting a drawing that uses an undeclared `a:` prefix made Word refuse to open the file ("Word experienced an error trying to open the file"). Declaring `xmlns:a` on `<a:graphic>` fixed it. The pipeline's `assemble()` does add `xmlns:a` to the root (`NS_EXTRA`), but a local declaration is more robust — [PoC: inject_into_report.py, export_report.ps1]
- Diagrams are currently drawn by matplotlib helpers `box(ax, x, y, w, h, title, body, kind)` and `arrow(ax, p0, p1)`. The layout is computed explicitly in axis units (e.g. the snake layout in `figure_data_flow`). Other functions: `sequence()`, `figure_upload_flow`, `figure_query_flow`, `figure_erd` with `_fk_arrow` — [scripts/build_system_figures.py lines 82–141, 250, 426, 448](../../scripts/build_system_figures.py)

### Inferences
- The least invasive design keeps the layout code and adds a second renderer. Each diagram function emits a neutral list of primitives (`Box(x,y,w,h,title,body,kind)`, `Arrow(p0,p1,kind)`), and that list goes either to matplotlib (PNG, unchanged) or to an OOXML emitter. The geometry stays in one place, and the existing tests that check diagram content (values taken from code: suffixes, MB limit, window/hop) can test the primitive list.
- The diagram paragraph should bypass Pandoc entirely, being emitted by a marker handler. Otherwise Pandoc would have to pass raw OpenXML through (`` ```{=openxml} `` blocks), which is possible but harder to keep in sync.

### Gaps
- `build_final_figures.py` was not inspected in detail. It is mostly charts, which should stay PNG or become native Word charts, which is a different topic.

## 2. OOXML options for editable diagrams (wpg group, wpc canvas, VML, SmartArt, connectors)

### Takeaway
Use DrawingML Word-processing shapes (`wps:wsp`) inside either an inline **group** (`wpg:wgp`) or an inline **drawing canvas** (`wpc:wpc`), each wrapped in `wp:inline` → `a:graphic` → `a:graphicData`. Both opened in Word 365 **without** any `mc:AlternateContent`/VML fallback. They rendered correctly, exported to PDF with selectable Vietnamese text, and came out editable: each box is a separate shape with a text box, and each arrow is a connector. Connector links (`a:stCxn`/`a:endCxn`) were honored (`BeginConnected=True`) **only after all `cNvPr` ids in the document were unique**. VML-only is legacy, and SmartArt is impractical.

### Cited Findings
- Spec: a group is `drawing → anchor|inline → graphic → graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" → wgp`. The listed fallback is a VML `pict` — [MS-ODRAWXML 2.2.7.4 DrawingML Groups in WordprocessingML](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-odrawxml/d97ae943-93d6-47ff-a261-6fca341fc5a8)
- Spec example of a canvas: `graphicData uri=".../wordprocessingCanvas"` → `wpc:wpc` with `wpc:bg`, `wpc:whole`, then `wps:wsp` children (each with `wps:cNvPr id name`, `wps:cNvSpPr txBox="1"`, `wps:spPr`, `wps:txbx/w:txbxContent`, `wps:bodyPr`) and `wpg:wgp` children (`wpg:cNvPr`, `wpg:cNvGrpSpPr`, `wpg:grpSpPr`) — [MS-ODRAWXML 3.7.2 Group and Linked Shapes within a Canvas](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-odrawxml/42d8d27f-4406-46d0-8238-3e209656f85f)
- `wps:cNvCnPr` is the connector non-visual properties slot of CT_WordprocessingShape — [MS-DOCX/ODRAWXML CT_WordprocessingShape](https://msdn.microsoft.com/en-us/library/69190647-27d1-4890-8089-a8aca57becb9). Its optional children are `a:cxnSpLocks`, `a:stCxn`, `a:endCxn` (attributes `id` = target shape id, `idx` = connection site) — [ECMA-376 cNvCxnSpPr reference (docx4j mirror)](https://webapp.docx4java.org/OnlineDemo/ecma376/DrawingML/cNvCxnSpPr_2.html)
- The template's own Word-authored connector uses `<wps:cNvCnPr><a:cxnSpLocks noChangeShapeType="1"/></wps:cNvCnPr>` + `prstGeom prst="straightConnector1"` + `<a:ln w="12700">…<a:tailEnd/></a:ln>`, inside `mc:Choice Requires="wps"` with a VML `v:shape` fallback — [PoC inspection of report/Mau bao cao KLTN_DS.docx]
- **[PoC] Plain inline `wpg` and plain inline `wpc` (no AlternateContent, no VML) open in Word 365 without error.** Word COM reports them in `Document.Shapes` (not `InlineShapes`): group `Type=6` (msoGroup), canvas `Type=20` (msoCanvas), `WrapFormat.Type=7` (wdWrapInline). Each has 5 items: 3 text boxes with text `Times New Roman 12`, and 2 connectors (`Connector=True`). `AlternativeText` equals `wp:docPr/@descr` — [PoC: make_poc.py + inspect_shapes.ps1]
- **[PoC] Connector links:** with duplicate ids (group children 1–5 and canvas children 1–5 in the same document), every connector reported `BeginConnected=False`. When Word re-saved the file, it rewrote the links to `<a:stCxn id="4294967295" …>` (unresolved) and renumbered all ids randomly. With document-unique ids (11–15 and 21–25), every connector, in the group and in the canvas, reported `BeginConnected=True`, `EndConnected=True`, `BeginConnectedShape=Box 11`, `BeginConnectionSite=4` (COM 1-based; XML `idx="3"` = right side of `rect`) — [PoC: poc.docx vs poc2.docx]
- **[PoC] On save, Word itself wraps every wps/wpg/wpc drawing in `mc:AlternateContent` with `mc:Choice Requires="wpc"|"wpg"`, and generates a VML `mc:Fallback`.** It does not need one on input — [PoC: poc_resaved.docx — 4 AlternateContent, 4 Fallback]
- Microsoft: connectors stay attached while the user moves shapes only inside a drawing canvas, "insert the shapes and connector in a new drawing canvas" — [Microsoft Learn: A connector does not move when you move a shape in Word](https://learn.microsoft.com/en-us/office/troubleshoot/word/connector-not-move-with-shapes)
- `CT_WordprocessingGroup` can contain `wsp`, `grpSp` (nested group), `pic`, `graphicFrame` — [MS-ODRAWXML CT_WordprocessingGroup](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-odrawxml/c89701a2-99ac-4948-b84f-1eaecc69dfa0)

Minimal tested XML ([PoC] `make_poc.py`; EMU: 1 cm = 360000, 1 pt = 12700, 1 twip = 635; text width of the thesis template 8787 twip = 5,579,745 EMU):

```xml
<!-- paragraph holding the diagram (pipeline: style FigurePara + keepNext) -->
<w:p><w:pPr><w:pStyle w:val="FigurePara"/><w:keepNext/></w:pPr>
 <w:r><w:drawing>
  <wp:inline distT="0" distB="0" distL="0" distR="0">
   <wp:extent cx="5500000" cy="640000"/>
   <wp:effectExtent l="0" t="0" r="0" b="0"/>
   <wp:docPr id="900101" name="Diagram 900101" descr="Sơ đồ ba bước: tải lên, phát hiện, truy vấn"/>
   <wp:cNvGraphicFramePr/>
   <a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
    <a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup">
     <wpg:wgp>
      <wpg:cNvGrpSpPr/>
      <wpg:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="5500000" cy="640000"/>
        <a:chOff x="0" y="0"/><a:chExt cx="5500000" cy="640000"/></a:xfrm></wpg:grpSpPr>

      <!-- rectangle with text -->
      <wps:wsp>
       <wps:cNvPr id="11" name="Box 11"/><wps:cNvSpPr/>
       <wps:spPr>
        <a:xfrm><a:off x="0" y="0"/><a:ext cx="1500000" cy="640000"/></a:xfrm>
        <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        <a:solidFill><a:srgbClr val="F2F2F2"/></a:solidFill>
        <a:ln w="12700"><a:solidFill><a:srgbClr val="000000"/></a:solidFill></a:ln>
       </wps:spPr>
       <wps:txbx><w:txbxContent>
        <w:p><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
          <w:ind w:left="0" w:right="0" w:firstLine="0"/><w:jc w:val="center"/></w:pPr>
         <w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:cs="Times New Roman"/>
           <w:sz w:val="24"/></w:rPr><w:t xml:space="preserve">Tải âm thanh lên</w:t></w:r></w:p>
       </w:txbxContent></wps:txbx>
       <wps:bodyPr rot="0" vert="horz" wrap="square" lIns="72000" tIns="36000" rIns="72000" bIns="36000"
                   anchor="ctr" anchorCtr="0"><a:noAutofit/></wps:bodyPr>
      </wps:wsp>
      <!-- … Box 12, Box 13 at x=2000000, 4000000 … -->

      <!-- arrow / connector (horizontal, left→right) -->
      <wps:wsp>
       <wps:cNvPr id="14" name="Arrow 14"/>
       <wps:cNvCnPr><a:stCxn id="11" idx="3"/><a:endCxn id="12" idx="1"/></wps:cNvCnPr>
       <wps:spPr>
        <a:xfrm><a:off x="1500000" y="320000"/><a:ext cx="500000" cy="0"/></a:xfrm>
        <a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>
        <a:ln w="12700"><a:solidFill><a:srgbClr val="000000"/></a:solidFill>
          <a:tailEnd type="triangle" w="med" len="med"/></a:ln>
       </wps:spPr>
       <wps:bodyPr/>
      </wps:wsp>
     </wpg:wgp>
    </a:graphicData>
   </a:graphic>
  </wp:inline>
 </w:drawing></w:r>
</w:p>
```

Canvas variant ([PoC], also works): `graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"` containing `<wpc:wpc><wpc:bg/><wpc:whole/> …same wps:wsp children… </wpc:wpc>`. It has no `grpSpPr`, and child offsets are in EMU relative to the canvas, whose size is `wp:extent`.

Required namespaces (on the root or locally): `w`, `wp` (`http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing`), `a`, `wps` (`http://schemas.microsoft.com/office/word/2010/wordprocessingShape`), `wpg` (`…/2010/wordprocessingGroup`), `wpc` (`…/2010/wordprocessingCanvas`). `mc` and `wp14`/`w14` are needed only if those attributes or elements are used. The PoC root had `mc:Ignorable="w14 wp14"` and did not list wps/wpg/wpc as ignorable. That is correct, because Word must understand them, and Word writes them under `mc:Choice Requires=` instead.

Schema order inside `wps:wsp`: `cNvPr?`, `cNvSpPr | cNvCnPr`, `spPr`, `style?`, `extLst?`, `txbx | linkedTxbx`?, `bodyPr` ([MS-ODRAWXML canvas example](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-odrawxml/42d8d27f-4406-46d0-8238-3e209656f85f) shows this order).

Preset `rect` connection sites: idx 0 = top, 1 = left, 2 = bottom, 3 = right. [PoC] confirmed that idx 3 maps to the right side (COM site 4).

### Inferences
- The **canvas** (`wpc`) is the better choice for diagrams people will edit later: per Microsoft, connectors stay glued only inside a canvas. The **group** (`wpg`) is fine for "edit text / restyle" and is slightly simpler. Both render identically.
- **Legacy VML** (`w:pict`/`v:shape`) is unnecessary for Word 2010+. Word generates the fallback itself on save. Writing VML by hand doubles the code for no benefit.
- **SmartArt (`dgm`)** needs separate data, layout, style and colors parts plus a cached drawing. It does not fit free-form flowcharts, sequence lanes or ERDs. Skip it.
- Ids must be unique across the whole document. The pipeline should allocate `docPr` ids and `cNvPr` ids from one counter (e.g. starting at 900000), well above the low ids Pandoc gives pictures.

### Gaps
- Not tested: elbow connectors (`bentConnector3` with `adj1`), arrows going right→left or bottom→top (these need `a:xfrm flipH="1"`/`flipV="1"` with positive `ext`), and diagonal lines. These follow standard DrawingML but were not opened in Word here.
- Not tested interactively: whether dragging a box inside the **group** keeps the connector glued. COM reported the links as connected in both containers. Microsoft's article implies live re-routing only in a canvas.
- I found no Microsoft statement that a plain (non-AlternateContent) `wpg`/`wpc` is officially supported on input. Support is shown here only empirically, on Word 365 / 27-11-2026.

## 3. Inline vs anchored, page flow, captions, and PDF export

### Takeaway
Use **inline** (`wp:inline`) diagrams in their own `FigurePara` paragraph with `keepNext`, which is exactly how the PNGs are placed today. An inline drawing behaves like one large character: it flows with the text, cannot split across pages, stays with the caption through `keepNext`, and exported to PDF correctly with selectable Vietnamese text. Anchored (`wp:anchor` + `wrapTopAndBottom`) adds positioning pitfalls and gains nothing here.

### Cited Findings
- [PoC] Inline `wpg` and `wpc` diagrams, followed by caption paragraphs with `SEQ Hình`, gave PDF captions "Hình 1 …" and "Hình 2 …" after `Fields.Update()` and `ExportAsFixedFormat(…, 17)`. Boxes, text and arrowheads render as expected in `poc-1.png` — [PoC: check_word.ps1]
- [PoC] PDF text extraction (`pdftotext`) returns the box labels as real text ("Tải âm thanh lên", "Phát hiện sự kiện (SED)", "Lưu và truy vấn RAG"). The PDF embeds TimesNewRomanPSMT as a CID font, so the diagram text is searchable and selectable, unlike the PNG — [PoC: poc.pdf, pdffonts]
- [PoC] Injected into a copy of the real 131-page thesis DOCX: Word opened it, updated fields, TOC and TOF, and exported the PDF. The diagram had `WrapFormat.Type=7`, 5 group items. Page count was unchanged at 131 — [PoC: export_report.ps1 output "pages=131 … diagram wrap=7 … items=5 / pdf ok"]
- Word VBA: `wdWrapInline = 7` "Places shapes in line with text"; `wdWrapTopBottom = 4` — [Microsoft Learn WdWrapType](https://learn.microsoft.com/en-us/office/vba/api/word.wdwraptype)

### Inferences
- The existing CAP handler only string-replaces `<w:pStyle w:val="FigurePara"/>` in `out[-1]` to add `keepNext`. A diagram paragraph emitted with that style works unchanged. Text-box paragraphs inside it must **not** use `FigurePara`, or the replace would also hit them. Use explicit `pPr` or a dedicated `DiagramText` style.
- The table of figures is built from Caption/SEQ fields, so diagrams are listed just like images.
- A diagram taller than the page area would be clipped, exactly as an oversized image is. Keep the diagram height at or below about 22 cm (A4 text height) and split large flows (e.g. data flow + storage branch) into two figures if needed.

### Gaps
- Anchored (`wp:anchor`, `wrapTopAndBottom`, `positionV relativeFrom="paragraph"`) was not tested. I found no source comparing its PDF fidelity with inline.

## 4. Word COM automation alternative (Shapes.AddShape / AddCanvas / AddConnector)

### Takeaway
COM can build the same objects with true glued connectors (`CanvasShapes.AddConnector` + `ConnectorFormat.BeginConnect/EndConnect`). From PowerShell and VBScript late binding, however, `BeginConnect` failed with **type mismatch** on this machine. `pywin32` is not installed in `.venv`. `ConvertToInlineShape` cannot convert shapes that hold text. COM is slow, needs Word, and is harder to keep reproducible. Raw XML is the better fit, and Word COM should be kept for the final field-update/PDF step as today.

### Cited Findings
- `CanvasShapes.AddConnector(Type, BeginX, BeginY, EndX, EndY)` returns a connector Shape in a drawing canvas. The example uses `docNew.Shapes.AddCanvas(Left, Top, Width, Height)` then `shpCanvas.CanvasItems.AddConnector` — [Microsoft Learn CanvasShapes.AddConnector](https://learn.microsoft.com/en-us/office/vba/api/word.canvasshapes.addconnector)
- A new connector is not attached to anything. `BeginConnect`/`EndConnect` attach its ends (Excel doc; the Office Shape model is shared) — [Microsoft Learn Excel Shapes.AddConnector](https://learn.microsoft.com/office/vba/api/excel.shapes.addconnector)
- `Shape.ConvertToInlineShape` converts "only shapes that represent pictures, OLE objects, or ActiveX controls". "Shapes that support attached text cannot be converted to inline shapes" — [Microsoft Learn Shape.ConvertToInlineShape](https://learn.microsoft.com/en-us/office/vba/api/word.shape.converttoinlineshape)
- Inline placement of a shape or canvas goes through `WrapFormat.Type = wdWrapInline (7)` — [Microsoft Learn WdWrapType](https://learn.microsoft.com/en-us/office/vba/api/word.wdwraptype)
- [PoC] PowerShell: `$c.ConnectorFormat.BeginConnect($shape, 4)` → "Cannot convert … __ComObject … to type ref". `InvokeMember` → `DISP_E_TYPEMISMATCH`. VBScript `cscript` → "Type mismatch: 'ConnectorFormat.BeginConnect'", even with `(shape)` ByVal. Each failed run also left a hidden `WINWORD.EXE` behind, which had to be killed — [PoC: com_canvas.ps1, com_canvas.vbs]
- [PoC] `pywin32` (`win32com`) is not available in the project `.venv` or the system Pythons 3.12 — [PoC check]

### Inferences
- COM pros: the result is exactly what Word itself would write, and it can use Word's autofit and real routing. COM cons: it is non-deterministic (Word assigns random ids and paraIds), slow (tens of seconds per Word start), fragile (orphan processes, ByRef marshalling), and needs Word on every build machine (CI on Linux cannot build). It also sits outside the existing "XML strings + tests" architecture.
- If COM is ever needed for connectors, VBA inside a macro-enabled helper, or `pywin32` with early binding (`gencache.EnsureDispatch`), would likely avoid the ByRef marshalling problem. That is untested.

### Gaps
- Not verified whether `pywin32` early binding fixes `BeginConnect`, because pywin32 is not installed here.

## 5. Libraries and other routes

### Takeaway
No mainstream free Python library writes Word shapes. python-docx explicitly does not add shapes. Aspose.Words can, but it is commercial. Mermaid/draw.io/Visio paths produce images or need Visio. The realistic open-source path is a small in-house emitter of `wps`/`wpg`/`wpc` XML, about 150–250 lines, which fits this pipeline because it already writes raw OOXML strings.

### Cited Findings
- python-docx docs: adding shapes is not supported ("If you have an active use case, submit a feature request on the issue tracker"). Pictures go through `add_picture()` — [python-docx shapes.rst (Debian source mirror)](https://sources.debian.org/src/python-docx/1.2.0%2Bdfsg-3/docs/user/shapes.rst); `InlineShape` wraps only `wp:inline` pictures — [python-docx shape API](https://python-docx.readthedocs.io/en/latest/api/shape.html)
- Aspose.Words for Python via .NET has `GroupShape` and `DocumentBuilder.insert_group_shape`. "VML and DML shapes cannot be grouped together." It is commercial — [Aspose docs: Working with Group Shape](https://docs.aspose.com/words/python-net/how-to-add-group-shape-into-a-word-document); [insert_group_shape reference](https://reference.aspose.com/words/python-net/aspose.words/documentbuilder/insert_group_shape)
- draw.io converts Mermaid into draw.io shapes inside draw.io. I found no draw.io → docx native-shape export — [draw.io blog: Mermaid updates](https://www.drawio.com/blog/mermaid-updates/)
- OfficeCLI is said to render Mermaid as native Office shapes (`--render native`). The source is a third-party write-up and the tool was not verified — [instagit: OfficeCLI Mermaid to native shapes](https://instagit.com/iofficeai/OfficeCLI/officecli-diagram-rendering-mermaid-to-shapes/)
- Visio diagrams can be embedded and edited in Word, but this needs Visio (Plan 2 for the Word integration) — [Microsoft Support: Document Visio process diagrams in Word](https://support.microsoft.com/en-us/visio/document-visio-process-diagrams-in-word)

### Inferences
- LibreOffice (ODG → DOCX) was not researched in depth. Its DOCX shape export is a known source of fidelity bugs (see the LibreOffice bug trees in search results), and it would add a heavy dependency. Not recommended.
- An embedded EMF/SVG image is "ungroupable" in Word, which converts it to shapes, but that is a manual user action and not reproducible. Not recommended.

### Gaps
- OfficeCLI output was not tested. Its license and maturity are unknown.

## 6. Practical issues and recommendation

### Takeaway
**Recommendation:** add an OOXML backend for the box-and-arrow figures in `build_system_figures.py`:
- the data flow, LBR flow, deployment architecture, upload and query sequence flows, and ERD;
- inline `wpc` canvas, or `wpg` group; unique ids from one counter; `xmlns:a` declared on `a:graphic`;
- explicit text-box paragraph properties: zero indent, line 240, Times New Roman 11–12 pt;
- inserted through a `@@DIAGRAM:name@@` marker handler and followed by the existing `@@CAP:fig@@`.

Keep matplotlib for data charts. Keep the PNG renderer as a fallback and for tests.

### Cited Findings
- [PoC] **Template style leak:** inside the real thesis template, text-box paragraphs without explicit `pPr` inherited the body style's first-line indent and wrapped badly ("Tải âm thanh / lên" shifted right). Adding `<w:ind w:left="0" w:right="0" w:firstLine="0"/>`, `<w:spacing w:before="0" w:after="0" w:line="240"/>` and `<w:jc w:val="center"/>` fixed it (`inj-002.png` vs `inj2-002.png`) — [PoC: inject_into_report.py]
- [PoC] Vietnamese diacritics (ắ ằ ẳ ẵ ặ ơ ư đ) in `w:t` inside `w:txbxContent` render and extract correctly. The text must be XML-escaped (`html.escape`) and stored in UTF-8 — [PoC: poc.pdf/pdftotext]
- [PoC] The run font `Times New Roman` with `w:sz=24` (12 pt) was honored inside the boxes (COM `Font.Name`/`Font.Size`) — [PoC: inspect_shapes.ps1]
- [PoC] Alt text: `wp:docPr/@descr` appears as `Shape.AlternativeText` in Word (accessibility pane) — [PoC: inspect_shapes.ps1]
- The pipeline's text width is `TEXT_WIDTH = 8787` twip (A4 11906 − margins 1985 − 1134), i.e. 5,579,745 EMU maximum diagram width — [ooxml.py line 13](../../scripts/report_docx/ooxml.py)

### Inferences
- **Font sizes:** body text is 13 pt. Box text of 11–12 pt (`w:sz` 22–24) with box titles in bold matches the current matplotlib look. Use 10 pt (`sz=20`) for dense ERD columns.
- **Autofit:** use `<a:noAutofit/>` and size boxes from a text-length estimate. The current matplotlib code already uses fixed box sizes with manual line breaks (`\n`), so map each `\n` to a separate `w:p` or a `<w:br/>` in the text box. `spAutoFit` (grow box to text) is applied by Word only when text is edited, which is unverified. Do not rely on it for layout.
- **Line routing:** the current diagrams already compute arrow endpoints (snake layout, vertical drops). Emit straight connectors with explicit `xfrm` from those endpoints. Use `flipH`/`flipV` for leftward or upward arrows, and `bentConnector3` only where the PNG has elbows. With `stCxn`/`endCxn` set, users can drag boxes inside the canvas and Word re-routes.
- **Units:** convert the matplotlib axis units into EMU with one scale factor per figure, so the whole figure fits within 5,579,745 EMU.
- **Determinism and tests:** raw XML strings are byte-deterministic, unlike COM output. Unit tests can assert box count, the texts (the same facts the PNG tests check), id uniqueness, and well-formedness (parse with `xml.etree` after wrapping in a root declaring all namespaces). The final Word open/PDF step already exists in `update_docx_fields.ps1`.
- **Checker:** `<w:drawing>` count is unchanged per figure. If the checker ever counts `pic:pic` or media files, it will see fewer images. That is expected, and the checker should count FigurePara paragraphs instead.
- **Word re-save:** `update_docx_fields.ps1` saves through Word. Word will renumber ids, add `mc:AlternateContent` + VML fallback, and keep connector links, as long as the ids were unique on input.

### Gaps
- Not measured: how the current matplotlib figures map in effort per figure. The sequence diagram, with lifelines and lanes, and the ERD, with tables as stacked rectangles or a single text box with a table inside, are the most work. A `w:tbl` inside `w:txbxContent` is allowed in WordprocessingML but was not tested here.
- Not tested: LibreOffice or Google Docs rendering of plain (no-fallback) wps shapes. This is irrelevant if the deliverable is always opened and re-saved by Word first, as the pipeline does.
