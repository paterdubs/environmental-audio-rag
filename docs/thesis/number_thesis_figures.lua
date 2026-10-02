local chapter_number = 0
local figure_number = 0

local function page_break()
  return pandoc.RawBlock(
    "openxml",
    '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'
  )
end

function Header(header)
  if header.level ~= 1 then
    return nil
  end

  chapter_number = chapter_number + 1
  figure_number = 0
  return { page_break(), header }
end

function Figure(figure)
  figure_number = figure_number + 1
  local caption = {
    pandoc.Str("Hình"),
    pandoc.Space(),
    pandoc.Str(chapter_number .. "." .. figure_number .. "."),
    pandoc.Space(),
  }

  if #figure.caption.long > 0 then
    for _, inline in ipairs(figure.caption.long[1].content) do
      table.insert(caption, inline)
    end
  end

  figure.caption.long = { pandoc.Plain(caption) }
  return figure
end
