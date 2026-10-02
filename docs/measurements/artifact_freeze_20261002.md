# Đóng băng artifact báo cáo

> Sinh bởi `scripts.freeze_artifacts`; chỉ đọc file hiện có, không chạy lại huấn luyện hay đánh giá. `MISSING` là thiếu trên máy hiện tại, không phải hash bịa.

Git lúc bắt đầu: `292571d79929ee5e3c06a3acfa45062c89dd1510` · dirty=False

## Run và ensemble

| Hệ thống | Run | Artifact có/thiếu |
|---|---|---:|
| v1 A (scratch) | `sed_polyphonic_20260923T173234Z` | 5/0 |
| v1 B (AudioSet) | `sed_polyphonic_20260924T054531Z` | 7/0 |
| v1 C (AudioSet→DataSEC) | `sed_polyphonic_20260924T061000Z` | 7/0 |
| v1 ensemble C | `sed_ensemble_C_clean_20260925T045631Z` | 14/0 |
| v2 B | `sed_polyphonic_20260926T033312Z` | 10/0 |
| v2 ensemble B | `sed_ensemble_v2_20260926T155630Z` | 12/0 |
| C-v2 ensemble | `sed_ensemble_cv2_20260926T205405Z` | 11/0 |
| T2a ensemble | `sed_ensemble_t2a_20260927T141952Z` | 11/0 |
| T2b ensemble (served f2 source) | `sed_ensemble_t2b_20260927T200914Z` | 11/0 |
| S11 focal ensemble | `sed_ensemble_s11_focal_t2b_20260928T185207Z` | 11/0 |
| S13 f2 test output | `sed_ensemble_s13_f2_20260929T045053Z` | 5/0 |

## SHA-256 và sự tồn tại

| Nhóm | Đường dẫn | Kiểu | Tồn tại | SHA-256 |
|---|---|---|:---:|---|
| v1 A (scratch) | `ml/runs/sed_polyphonic_20260923T173234Z/manifest.json` | run_manifest | có | `9c9eb5452573b8e358ca22fdfdaedaa4e25a093309761868f3bfea74dc5435ec` |
| v1 A (scratch) | `ml/runs/sed_polyphonic_20260923T173234Z/predictions/dev.npz` | prediction | có | `fc01a3e14bcf86a9ff016b024dcb7a20d9da4de75a05a8a214737ef0a9636bc0` |
| v1 A (scratch) | `ml/runs/sed_polyphonic_20260923T173234Z/predictions/test.npz` | prediction | có | `664b61cc72b7905693151f10d680c4cafca4d2826efb39f4f66cbaa3d8f1a04a` |
| v1 A (scratch) | `ml/runs/sed_polyphonic_20260923T173234Z/postproc.json` | postproc_or_sebb | có | `88bd1df200053c89d121db04d45896cdee7434dc1bd83a4802a445dd0607e8e9` |
| v1 A (scratch) | `ml/runs/sed_polyphonic_20260923T173234Z/checkpoints/best.pt` | best_checkpoint | có | `2f0fc26f732b36c90590e2313aeadf95c847d33803e6370263145ddb204227fc` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/manifest.json` | run_manifest | có | `952d6fd3112fa9ef73a95f359168b561ae909659d5dc971c086328c7b48ee703` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/predictions/dev.npz` | prediction | có | `9cd0e7b74aca16d15921de27af390bfa29f5ee7c6324824fdf347067f83ef28f` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/predictions/test.npz` | prediction | có | `42818510d015469a678db5530eee37f51f8b01fd53c6c150a708e870a32fa430` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/postproc.json` | postproc_or_sebb | có | `3caf552f87c17b2e5b8082466a3823fcab639cf6ed49ad045b612107236522ae` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/postproc_cv.json` | postproc_or_sebb | có | `384b1c588f27b9ba572e1b8fd23d56d4a7e971f665bba69e56f3d2f046377fa9` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/postproc_cv_selection.json` | postproc_or_sebb | có | `e8e7e98c364f5ea7df4ad48cff26dd4d9da0057e1977b0cd9a61bcf8dd06a670` |
| v1 B (AudioSet) | `ml/runs/sed_polyphonic_20260924T054531Z/checkpoints/best.pt` | best_checkpoint | có | `428896df645e84180e0e28308665c698b5d89c22fe2348c96760e858e37dcdd4` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/manifest.json` | run_manifest | có | `e29ae57720789624867090b98643c2e312c814a9c901504feca0ff351a65d692` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/predictions/dev.npz` | prediction | có | `eb189a28ddcd0eed3f040e559b8d1cf58fa56d4db0efab364a8750b6b2c3524c` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/predictions/test.npz` | prediction | có | `8561bd0639051114125cc130e8a40768cde79c5e1aa37c4990bcc37c11ffc0b8` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/postproc.json` | postproc_or_sebb | có | `0dd954c84218d38e91879f64040110a47a09d84334b486765ed8a987d7b8bac1` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/postproc_cv.json` | postproc_or_sebb | có | `d929c9073eba8c15bd90e986f46e549964ac86e8e137cee3eb894daf4e05fd7b` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/postproc_cv_selection.json` | postproc_or_sebb | có | `ee5aaaef637350b06c3035a17040b41fb7eef05b038c673ed0bd210595ff8da0` |
| v1 C (AudioSet→DataSEC) | `ml/runs/sed_polyphonic_20260924T061000Z/checkpoints/best.pt` | best_checkpoint | có | `39dd7fe721d5da470f328763c6e26a04a2fa3f521304246eb6e8f7e0bc4ca229` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/manifest.json` | run_manifest | có | `27f84d8685faab1070751adf241a5ebb3ee5ca3fb4153e5dfc955be3c7c14f05` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/predictions/dev.npz` | prediction | có | `4af86f6d7966773007693e451274bc3608e1b857981ce1b6a78bcd8b300e9574` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/predictions/test.npz` | prediction | có | `ea87a2ea6c52159729780715825cbac616f756f07643c1d76f7ab1c5fca99f1e` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/postproc.json` | postproc_or_sebb | có | `72b89077c7aa6e071d86c4330311e6d6db8e63a60774a86d91b759b4b31ee050` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/postproc_cv.json` | postproc_or_sebb | có | `d05c7e00ba3c9df7190f88c9a711e4c39d9c1241f40df0ee2556780ef2a1962f` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `d05c7e00ba3c9df7190f88c9a711e4c39d9c1241f40df0ee2556780ef2a1962f` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/postproc_cv_selection.json` | postproc_or_sebb | có | `3e34c09dcd4756fc14148886f8c28aaa18afcc25d2fd5b08a98d53e2e28e5398` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `a6d9bea572b4ee54474924ae633db53227e7b07ecb15e85d338b4e8fb05653e3` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/sebb_cv_selection.json` | postproc_or_sebb | có | `595086477ed8d08c2bef9674d07252982bd52270739ec2a4ae51db4939e87c4e` |
| v1 ensemble C | `ml/runs/sed_ensemble_C_clean_20260925T045631Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `827111907cfdd9f5bf536fa5b639556178797c6166edb1a726382a1103a806df` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T033537Z/checkpoints/best.pt` | best_checkpoint | có | `33b48f66954aa03013e9e18432c0650cf8bbe1b020d3762c2e0a84e5e9f38938` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T061000Z/checkpoints/best.pt` | best_checkpoint | có | `39dd7fe721d5da470f328763c6e26a04a2fa3f521304246eb6e8f7e0bc4ca229` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T072736Z/checkpoints/best.pt` | best_checkpoint | có | `62333fa6c40b2030b647cb97965d17febcdc8c5438657b7fe632806f12973124` |
| v1 ensemble C | `ml/runs/sed_polyphonic_20260924T080715Z/checkpoints/best.pt` | best_checkpoint | có | `99b7c6f0783552bc591d4fb709e594488c424129b74e86204fd50e8cc88c94ab` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/manifest.json` | run_manifest | có | `3b23ab0658c219d249a14118185cb427e8e65c5f93e76d18baaf4ffd287b3e46` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/predictions/dev.npz` | prediction | có | `afda4e5c58ccaed641968855a5fa694b2a176ffa61bad05b71711663092e8c88` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/predictions/test.npz` | prediction | có | `15fa4cef90b561c639417bd761c41db8f53b778e1b3177005a362147e307c555` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/postproc_cv.json` | postproc_or_sebb | có | `49d2f412420f33e49824c227c59a194c94d513a4eccb520039640809c2c8c176` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `49d2f412420f33e49824c227c59a194c94d513a4eccb520039640809c2c8c176` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/postproc_cv_selection.json` | postproc_or_sebb | có | `39811afb908831172e8e15bb1bed1dc4d89d323efe71849bc0b0a26e3f6ecbcd` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `428a5fea7ccd6c17a448d43019bd56f362e70d8828215d1ffb942aec82adaea0` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/sebb_cv_selection.json` | postproc_or_sebb | có | `afeaa5437bb5bf220ae8b1136452e4e5f6dbf7a69fd361bb97d13bc3e3480aa5` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `bd6b7951dabaccfeb2460ac740196c3eceae50f3820ccb359f9dff7fd3f39275` |
| v2 B | `ml/runs/sed_polyphonic_20260926T033312Z/checkpoints/best.pt` | best_checkpoint | có | `4c340341c3bd788a42ea542e27c50dc9e2c1efcf09336fdd254d5e2956d52f8d` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/manifest.json` | run_manifest | có | `b645368cd003d713de53050e6a9a4de86bb930618616b557fe64bc8b2ab590e9` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/predictions/dev.npz` | prediction | có | `55ed1fa87d486d7813c9fcae65c863e13039f00dd1ad69425b205787df3abe18` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/predictions/test.npz` | prediction | có | `86554be67758970d32da8e427feb7e921fb1e7960670d23ed4fe171a864a7597` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/postproc_cv.json` | postproc_or_sebb | có | `765f4141fb840249e3765e410d982c5f64c3c3a1a18e338cd4a0b9fb560aa2d6` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `765f4141fb840249e3765e410d982c5f64c3c3a1a18e338cd4a0b9fb560aa2d6` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/postproc_cv_selection.json` | postproc_or_sebb | có | `bba2b5ec94c801bfe26393935b2903330ed8f12c19e82fd7f9e39dbfd54f5a6a` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `2e86c3e5aa486e11f01ca87e99dcf071609eb640dcb996618a8a87d7909902d0` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/sebb_cv_selection.json` | postproc_or_sebb | có | `a7bd0fb402589e5167eb15aa3d947ff9b8afe4fdbcc0caa0faf07196a0f7a9fe` |
| v2 ensemble B | `ml/runs/sed_ensemble_v2_20260926T155630Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `a4cd11307dc4aefbddb4d2ed9bcde09c48c3bba4431debc25a236e02d7ba9020` |
| v2 ensemble B | `ml/runs/sed_polyphonic_20260926T033312Z/checkpoints/best.pt` | best_checkpoint | có | `4c340341c3bd788a42ea542e27c50dc9e2c1efcf09336fdd254d5e2956d52f8d` |
| v2 ensemble B | `ml/runs/sed_polyphonic_20260926T053024Z/checkpoints/best.pt` | best_checkpoint | có | `2c7fa6ade03840ba6a3f1a199c452aaca2ed16b5406273f643fdbb68db4f61d9` |
| v2 ensemble B | `ml/runs/sed_polyphonic_20260926T064832Z/checkpoints/best.pt` | best_checkpoint | có | `fbd9cf2ad81688a2df60c45da65012b78a63ef3a620e3f0adf96c6a07167f0dc` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/manifest.json` | run_manifest | có | `d4da4f19529a12813e95095c5ec75847397b2579e2af3bb02438448bc17207bb` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/predictions/dev.npz` | prediction | có | `e1b5a0f42dfd5c3eac8032fe6bb69ef0db3babad7c4c2e5a9fde1be20f61597b` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/postproc_cv.json` | postproc_or_sebb | có | `7398b397957754cef9ae7050d2c8fc228d88c10b4c187fbf153fe54a57e5c6b5` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `7398b397957754cef9ae7050d2c8fc228d88c10b4c187fbf153fe54a57e5c6b5` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/postproc_cv_selection.json` | postproc_or_sebb | có | `a060ce0b79cf830728e58a5595d7c60b397863da0a6ff17475b0723aee5f9394` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `f3e8fe2949538205284524508c800f7622eba65a3307a9c1230473395cab128c` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/sebb_cv_selection.json` | postproc_or_sebb | có | `8faeeeb6beced5cdc85e328d865af989aad1789884b6c7e336024ce8bd0dd88d` |
| C-v2 ensemble | `ml/runs/sed_ensemble_cv2_20260926T205405Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `5c8e889b8218d0219b4ec5f35824a4974222de56601cd79519766060ed976452` |
| C-v2 ensemble | `ml/runs/sed_polyphonic_20260926T161726Z/checkpoints/best.pt` | best_checkpoint | có | `dc357762d087ff6b8326163cdfc2785461c98f6e62e448f77badba241c04a20c` |
| C-v2 ensemble | `ml/runs/sed_polyphonic_20260926T172229Z/checkpoints/best.pt` | best_checkpoint | có | `cfdc656a8d119450a17a2e4176d9ae3b81f4d8b4b788bdfda672aabd6477e6d4` |
| C-v2 ensemble | `ml/runs/sed_polyphonic_20260926T185208Z/checkpoints/best.pt` | best_checkpoint | có | `6931b599931e128bdddb7058daf6e7b9be9ad73b6bf58ceb62e6d782c2057bc7` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/manifest.json` | run_manifest | có | `8d686d26d85741ab3aaf1b2c1d4672f1049cc427477018fe2ca0d4d19bde814a` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/predictions/dev.npz` | prediction | có | `5635f79f2a6bda6f1dc891bc7f2bdaeafcf866e32b550935880805c9ea618e4a` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/postproc_cv.json` | postproc_or_sebb | có | `8db423e54224d2c094252891979ecd7c91123db6aafe33ed3af035fe1b2e3c0c` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `8db423e54224d2c094252891979ecd7c91123db6aafe33ed3af035fe1b2e3c0c` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/postproc_cv_selection.json` | postproc_or_sebb | có | `ee049ad142e737344aced5293a56aac6ff4d813420f35e6e061a33b210124729` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `58c5afeacdd9af710ad8ae7ee9cefd98df23599da1fa4a2ca1327eeb1bcce050` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/sebb_cv_selection.json` | postproc_or_sebb | có | `38edef469384ff913fcc5d1fbabdb89d15f61d2cc0da5e1a0ff490694715c422` |
| T2a ensemble | `ml/runs/sed_ensemble_t2a_20260927T141952Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `d95de8e5c452dbbb9ebc7dc601225f9a141c0b1f74098f5695868bbe48a7a046` |
| T2a ensemble | `ml/runs/sed_polyphonic_20260927T064341Z/checkpoints/best.pt` | best_checkpoint | có | `f4190718826de3d5ad611a2ff617ce7517306962f73dd20235d8ab8392a385c5` |
| T2a ensemble | `ml/runs/sed_polyphonic_20260927T092605Z/checkpoints/best.pt` | best_checkpoint | có | `5f69972598923c33eed7ee0a0e04b32118d37514d331ace59dd6eb8512d3f1f2` |
| T2a ensemble | `ml/runs/sed_polyphonic_20260927T113910Z/checkpoints/best.pt` | best_checkpoint | có | `dbe017a7d24ddecf49fac8a4f1370c475b9ab4b90418024d8a1244df7595cc00` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/manifest.json` | run_manifest | có | `c21a71f64c32875e4bf7c0750ad762a24746dfa576ff6ec989dc9bc461c6cfdd` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/predictions/dev.npz` | prediction | có | `08b14a95edbda75585156e6c64ba86a73d4afd25371ec10c171482d2ee03bc2a` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/postproc_cv.json` | postproc_or_sebb | có | `6c2cdada49c2eaec48460b6b4d94dbf02ba3deabc0674746c1e08fadddaf11fd` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `6c2cdada49c2eaec48460b6b4d94dbf02ba3deabc0674746c1e08fadddaf11fd` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/postproc_cv_selection.json` | postproc_or_sebb | có | `7e8a2f16637c7188a4ba9ed513304e00b87f1802e10705fa9f6216ae235ceac3` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `d8def980349b0925c3c2e7b08412ac88dc46af65f2dbb31437d9028325e09053` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/sebb_cv_selection.json` | postproc_or_sebb | có | `9ee5bed95346f54a74b9cf047160b048923ae5f0f87870a9e2f3964fec5db8b8` |
| T2b ensemble (served f2 source) | `ml/runs/sed_ensemble_t2b_20260927T200914Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `7187bb30bd03c9d0096ef1679513080c4308fa9266721e0afed4bdb9e6c82ca0` |
| T2b ensemble (served f2 source) | `ml/runs/sed_polyphonic_20260927T172924Z/checkpoints/best.pt` | best_checkpoint | có | `5090beb60bbd38ae00396506d0d64d910de66dec914ddbf92f1c2bcf39561a8d` |
| T2b ensemble (served f2 source) | `ml/runs/sed_polyphonic_20260927T180358Z/checkpoints/best.pt` | best_checkpoint | có | `787e15395f05ef52d219e190286cba35b3d79e8681f974fc87410b825133663d` |
| T2b ensemble (served f2 source) | `ml/runs/sed_polyphonic_20260927T185137Z/checkpoints/best.pt` | best_checkpoint | có | `6bfa01b3217387c36f508a7f46d87db391e30060748db680a3bed08662e3a44f` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/manifest.json` | run_manifest | có | `c888a447e76ca6a2ecbfdfa5a33f93fe32c1020a33ae7d01567aed8a7f60f316` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/predictions/dev.npz` | prediction | có | `5dc73d082d11b8be4b40bd56a5b6b74d552998733ba42b0adef8b04af7de2ba2` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/postproc_cv.json` | postproc_or_sebb | có | `5ad788b03837e9d9f7553e81c5a8e37363eb0faf6b4d094c654f09a72847a0d2` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/postproc_cv_annotated.json` | postproc_or_sebb | có | `5ad788b03837e9d9f7553e81c5a8e37363eb0faf6b4d094c654f09a72847a0d2` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/postproc_cv_selection.json` | postproc_or_sebb | có | `aa2c4ea695b494f96ba33538c15142a0f93d57278519f2fdae4dcb414c4567ba` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/postproc_cv_selection_annotated.json` | postproc_or_sebb | có | `299295b6637f146d224fac7df2c97a9b4b1c0a18fbabdbdf930db1c3910c7f78` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/sebb_cv_selection.json` | postproc_or_sebb | có | `754ac73ce6bfae7c0b6d82eaa337c261e3bf094b75c0b453d913a9bf089ba87b` |
| S11 focal ensemble | `ml/runs/sed_ensemble_s11_focal_t2b_20260928T185207Z/sebb_cv_selection_annotated.json` | postproc_or_sebb | có | `1826ae546cbba285ca3f9d4061c06ae9e0f416e38037466432e6c3a251b39e1d` |
| S11 focal ensemble | `ml/runs/sed_polyphonic_20260928T165635Z/checkpoints/best.pt` | best_checkpoint | có | `e91cef7d466520c42456d707fbb387ca7267b94ac895f5e0529db1cb473e7654` |
| S11 focal ensemble | `ml/runs/sed_polyphonic_20260928T173526Z/checkpoints/best.pt` | best_checkpoint | có | `fea868afd66177743fb7545584f4ff5a6f5d279b39d27c161ebe10f230531388` |
| S11 focal ensemble | `ml/runs/sed_polyphonic_20260928T181509Z/checkpoints/best.pt` | best_checkpoint | có | `65b70c55516cc3cafe4c1833486417214aee1313a29aea3ff3415edf3a26d846` |
| S13 f2 test output | `ml/runs/sed_ensemble_s13_f2_20260929T045053Z/manifest.json` | run_manifest | có | `6e47cd6a272c972861db9078f74fcb53a4a82b0a7e064ed7259bac5cce1529fd` |
| S13 f2 test output | `ml/runs/sed_ensemble_s13_f2_20260929T045053Z/predictions/test.npz` | prediction | có | `86b4287d881b515020253d7e0880ecf61f0b39e1fd737bfe3a71243ae1af5dac` |
| S13 f2 test output | `ml/runs/sed_polyphonic_20260927T172924Z/checkpoints/best.pt` | best_checkpoint | có | `5090beb60bbd38ae00396506d0d64d910de66dec914ddbf92f1c2bcf39561a8d` |
| S13 f2 test output | `ml/runs/sed_polyphonic_20260927T180358Z/checkpoints/best.pt` | best_checkpoint | có | `787e15395f05ef52d219e190286cba35b3d79e8681f974fc87410b825133663d` |
| S13 f2 test output | `ml/runs/sed_polyphonic_20260927T185137Z/checkpoints/best.pt` | best_checkpoint | có | `6bfa01b3217387c36f508a7f46d87db391e30060748db680a3bed08662e3a44f` |
| checkpoint/cache ngoài | `artifacts/checkpoints/Cnn14_mAP=0.431.pth` | AudioSet_CNN14 | có | `7f0ea3a7ad9622f7bdc22439a750e04efdc1641bc4c930ff8727bb92d3141a69` |
| checkpoint/cache ngoài | `artifacts/checkpoints/BEATs_strong_1.pt` | BEATs | có | `db13a79ae90a0cfd0f9911a6a1d8cdb89324322bee642dcfe32de022123b8b54` |
| checkpoint/cache ngoài | `artifacts/checkpoints/frame_mn10_strong_1.pt` | frame_mn10 | có | `4a0fe320d5369987b772394c51881fb20a602967e6842f72f3e5c8181065ece7` |
| checkpoint/cache ngoài | `artifacts/llm/Qwen_Qwen3.5-9B-Q4_K_M.gguf` | Qwen_GGUF | có | `d784ce9eda1a5a7b51e8f705a9e6310844bf4f173654d115823c775fdea56d43` |
| checkpoint/cache ngoài | `artifacts/hf/models--BAAI--bge-m3` | tree | có | `3e942530b983ead63fecf1a36a34b8b581eccf464da7351e19c27f23ddb6b94c` |

## File nguồn đóng băng

| Đường dẫn | Tồn tại | SHA-256 |
|---|:---:|---|
| `data/splits/datased_polyphonic.frozen.json` | có | `c3d29189b5fcd3f407077d032cf48647dd731e695fa96e6b7e23a6f24861a1bf` |
| `ml/configs/taxonomy.yaml` | có | `67ca8a8c53278cd438d7d06a4ba09e277f3f9a6df99460bdbec1d3a927729a3a` |
| `ml/configs/caption_lexicon.yaml` | có | `184cdc6af18454a16b885f5cd8ece848c3e635df951f8edb1f8f1b794db2d578` |
| `ml/configs/caption_lexicon_vi.yaml` | có | `35ccf58cd888f53025bf7525e28bbaad0dc378ac912abdfd5e8bca886b67ac5e` |
| `ml/configs/caption_llm.yaml` | có | `94770dc649568c8b9617a9d1ced135e9abaf89a06a92dd4c92f44467937c91b8` |
| `ml/retrieval/query_set.py` | có | `3c406f0490a7a115c93af28725678761c11543bf3a285ebd55bd8620a9706a49` |
| `ml/captioning/constrained.py` | có | `469f2a2aca30839c0164ef13deb18aa845a21e5ff4f5b356019b9cace94f06ff` |
