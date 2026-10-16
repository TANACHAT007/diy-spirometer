# Builds the 7th IYS essay (Health sub-theme) as .docx following GUIDE BOOK rules:
# cover page (title, leader, members, institutions) -> Introduction -> Body -> Conclusion -> References -> Attachments;
# Times New Roman 12, page numbers, 3-10 pages from Introduction to Conclusion.
import os
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

H = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(H, '..', 'web', 'img')

TITLE = 'Spiro: A Low-Cost 3D-Printed IoT Spirometer with a Disposable Mouthpiece Made from Burned-Field Crop Residue'
SUB = 'Bridging air pollution, lung health and circular materials for communities that cannot reach a hospital spirometer'
LEADER = 'Puttitada Pruetchayakul (Bodindecha (Sing Singhaseni) School)'
MEMBERS = ('Pimnara Roongsetthavitr (International Community School); Suchanan Kittikraisak (The Newton Sixth Form); '
           'Natnicha Taepucharoen (Samsenwittayalai School); Nabhat Sethaudom (International Community School)')
INST = 'Bodindecha (Sing Singhaseni) School; International Community School; The Newton Sixth Form; Samsenwittayalai School'
ADVISOR = 'Tanachat S. (teacher / project advisor, not a competitor)'

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.54)
sec.top_margin = sec.bottom_margin = Cm(2.54)

st = doc.styles['Normal']
st.font.name = 'Times New Roman'; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')
st.paragraph_format.space_after = Pt(6); st.paragraph_format.line_spacing = 1.15
for name in ('Heading 1', 'Heading 2'):
    h = doc.styles[name]; h.font.name = 'Times New Roman'; h.font.bold = True
    h.font.color.rgb = None; h.font.size = Pt(14 if name == 'Heading 1' else 12)
    rf = h.element.rPr.rFonts
    for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
    for a in ('w:ascii', 'w:hAnsi', 'w:eastAsia', 'w:cs'): rf.set(qn(a), 'Times New Roman')
    h.paragraph_format.space_before = Pt(12); h.paragraph_format.space_after = Pt(4); h.paragraph_format.keep_with_next = True


def page_number_footer(section):
    p = section.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    for t, txt in (('begin', None), (None, 'PAGE'), ('end', None)):
        if t:
            e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), t); r._r.append(e)
        else:
            e = OxmlElement('w:instrText'); e.set(qn('xml:space'), 'preserve'); e.text = txt; r._r.append(e)
    r.font.name = 'Times New Roman'; r.font.size = Pt(12)


page_number_footer(sec)


def para(text, bold=False, italic=False, align=None, size=None, after=None, indent=True):
    p = doc.add_paragraph()
    if align == 'c': p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align != 'l': p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if after is not None: p.paragraph_format.space_after = Pt(after)
    r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    return p


def fig(path, caption, w=12.5):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(w))
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = c.add_run(caption); r.italic = True; r.font.size = Pt(11)


def table(rows, widths, header=True, size=10.5):
    t = doc.add_table(rows=len(rows), cols=len(rows[0])); t.style = 'Table Grid'
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.width = Cm(widths[j]); c.text = ''
            r = c.paragraphs[0].add_run(val); r.font.size = Pt(size); r.bold = header and i == 0
            c.paragraphs[0].paragraph_format.space_after = Pt(0)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


# ---------------------------------------------------------------- cover page
for _ in range(5): doc.add_paragraph()
para('7th International Youth Summit (IYS) 2026 - International Essay Competition', align='c', size=12, after=2)
para('Sub-theme: Health', bold=True, align='c', after=26)
para(TITLE, bold=True, align='c', size=18, after=10)
para(SUB, italic=True, align='c', size=13, after=36)
para('Team MEDTHAI', bold=True, align='c', size=13, after=2)
para('Team leader: ' + LEADER, align='c', after=2)
para('Members: ' + MEMBERS, align='c', after=2)
para('Institutions: ' + INST, align='c', after=2)
para('Advisor: ' + ADVISOR, align='c', after=2)
para('Country: Thailand', align='c', after=30)
para('Theme: "Bridging Ideas and Youth Creativity to Shape Solutions for Tomorrow\'s Challenges"', italic=True, align='c', size=11)
doc.add_page_break()

# ---------------------------------------------------------------- Introduction
doc.add_heading('1. Introduction', 1)
para('Every dry season, smoke from burning rice straw, stubble and sugarcane leaves settles over northern and central Thailand. '
     'The fine particles (PM2.5) in that smoke reach the deepest part of the lung. Breathing in them for years is linked to chronic '
     'cough, asthma and chronic obstructive pulmonary disease (COPD). A province-level modelling study of five residue crops estimated '
     'that open burning of crop residue costs Thailand roughly 524 billion baht in health and environmental damage, while the '
     'alternatives it tested (animal feed, fertiliser, leaving residue in the field, power generation) gave a net benefit [1]. '
     'Another Thai study found that burning all rice straw would raise health impacts by 81.1% compared with the business-as-usual case [2].')
para('Yet the people who breathe this smoke are often far from a hospital that owns a spirometer, the standard breathing test that '
     'measures how much air, and how fast, a person can blow out. Without that test, a smoker\'s cough, a farmer\'s wheeze or a child\'s '
     'asthma can go unmeasured for years. At the same time, the same fields that create the smoke produce a material that can be turned '
     'into something useful: fibre.')
para('This essay presents Spiro, a student-designed prototype that tries to connect these two problems. Spiro is a handheld spirometer '
     'whose measuring body is 3D-printed and cheap to build, whose results are sent to a phone or website, and whose single-use '
     'mouthpiece is planned to be moulded from the same crop residue that would otherwise be burned. We describe the design, the '
     'reasoning behind it, an online system for patients, doctors and administrators, and - just as importantly - what has not yet been '
     'proven. Spiro is a learning and screening prototype. It is not a certified medical device and must not be used for diagnosis.')

# ---------------------------------------------------------------- Body
doc.add_heading('2. Body', 1)
doc.add_heading('2.1 The problem and the gap', 2)
para('Spirometry is the test used to detect and follow obstructive lung disease; international standards from the American Thoracic '
     'Society and European Respiratory Society (ATS/ERS) define how it should be performed, including at least three acceptable '
     'blows that repeat within 0.15 L [3][4]. Commercial spirometers meet these standards but are designed for clinics. Our goal is '
     'more modest: a device that a school, a community health volunteer or a village health post could build and use for '
     'screening, and that passes results to a doctor. Research groups have already shown that printed venturi spirometers are '
     'feasible; one 2025 study reported about 1.5% error against a 2 L calibration pump for a 3D-printed venturi with an ESP32 [5]. '
     'What is missing in the literature we found is a low-cost design that also deals with infection control and waste, and that is '
     'paired with an accounts-based service connecting patient and doctor.')

doc.add_heading('2.2 Where Spiro comes from: versions 1 and 2', 2)
para('Spiro is not a first attempt. Our team previously built two working prototypes, version 1 and version 2, whose measuring and IoT '
     'system functioned as intended and which won an award in an earlier competition [award name, organiser and year - to be filled in by the team]. '
     'Version 3, presented here, keeps that proven approach to measurement and data transfer and changes the part that creates the most waste: the '
     'mouthpiece. Its goal is to turn agricultural waste into the single-use part that every patient needs, while the measuring unit is reused. '
     'The remainder of this section describes the version 3 design in detail.')
doc.add_heading('2.3 How version 3 works', 2)
para('Spiro uses a venturi: a tube that narrows to a throat. When air is blown through it, the air speeds up at the throat and its pressure '
     'drops. A Sensirion SDP810-500Pa differential-pressure sensor measures the pressure difference between the wide part (28 mm) and the '
     'throat (23 mm). Flow follows Q = K * sqrt(dP), and integrating flow over time gives volume. From one blow the firmware reports '
     'forced vital capacity (FVC), forced expiratory volume in one second (FEV1), their ratio and peak expiratory flow (PEF). '
     'A XIAO ESP32-S3 reads the sensor at 400 Hz, shows the result on a 1.28-inch round display with a speaker prompt, and sends it by '
     'Bluetooth Low Energy or Wi-Fi.')
fig(os.path.join(IMG, 'v_hero.png'), 'Figure 1. CAD render of the handheld unit on its magnetic charging dock (mouthpiece shown in the planned crop-residue colour).', 11)
para('The body is printed in PETG as ten parts held by M3 screws into brass heat-set inserts. The venturi tube lifts out and can be washed. '
     'Even small assembly details were designed to be buildable: for example, the push-button and status LED are soldered to a small '
     'daughter board first, the board is dropped onto two wall posts, and two M2 screws lock it, so no part is trapped behind printed '
     'features. The estimated material cost of the whole kit is about 3,100 baht (about USD 85) in our bill of materials; this is a '
     'design estimate, not a purchase receipt.')
fig(os.path.join(IMG, 'v_inside.png'), 'Figure 2. Transparent view of the internal parts: sensor, round display, battery, microcontroller and wiring.', 11)

doc.add_heading('2.4 From burned fields to the mouthpiece', 2)
para('Each person must blow into a clean mouthpiece, so a spirometer generates a stream of single-use parts. Our design makes the mouthpiece '
     'a separate, replaceable piece that the device counts (a reminder appears after 20 blows or 7 days). The prototype mouthpiece is '
     'printed in PETG to check size and fit, but it is not biodegradable. Our proposal for production is to replace it with moulded '
     'pulp made from field-burned residue.')
para('We deliberately chose rice straw and sugarcane leaves rather than bagasse. Bagasse, the fibre left after cane is crushed, is mostly '
     'burned inside the sugar mills as fuel to generate electricity (about 30.7 million tonnes in 2016 [6]), so it is not the waste that '
     'pollutes the air. The residue that is still burned in the open is the field residue: cane leaves and tops are estimated at about 20 '
     'million tonnes per year, of which about 12 million tonnes were open-burned [7], and rice straw makes up most of Thailand\'s '
     'openly burned crop residue [2]. Evidence that such fibre can be moulded is encouraging: a University of Bangor study found trays with up to 80% '
     'straw were stronger in tension than expanded polystyrene and lost about 20% of their mass in four weeks in unsterilised soil [8]; '
     'a Thai study moulded rice-straw and bagasse pulp with tapioca starch and reduced water absorption with a chitosan coating [9]. '
     'Disposable air tubes for spirometers made of cardboard, paper or other biodegradable materials are also described in patents [10], and a '
     'university student project used cardboard mouthpieces on a reusable body, reporting that 28 of 30 volume measurements met ATS '
     'accuracy limits after calibration [11].')
table([
    ['Stage', 'Material', 'Purpose', 'Status'],
    ['Prototype', 'PETG (3D-printed)', 'Check size, fit and airflow resistance', 'Used in the current design'],
    ['Production', 'Moulded pulp from rice straw / cane leaves', 'Compostable, uses field-burned residue', 'Proposal; supplier and hygiene testing needed'],
    ['Fallback', 'Standard cardboard spirometer mouthpiece', 'Available on the market today', 'Needs socket size check (ours 30.4 mm)'],
], [2.4, 4.6, 5.2, 3.8])
para('Two honest cautions apply. First, a mouthpiece is not a bacterial filter, so single-person use and hygiene rules still matter. '
     'Second, we found no peer-reviewed measurement of airflow resistance or accuracy for crop-residue pulp mouthpieces in a spirometer; '
     'the studies above support the material, not the medical use. That measurement is part of our plan.')

doc.add_heading('2.5 An online system for patients, doctors and administrators', 2)
para('Data are only useful if the right person can see them. We built a web service with three roles. A patient registers, blows into the '
     'device or follows the on-screen coaching, and sees a history and trend. A doctor, after approval by an administrator, '
     'uses a clinic mode that guides a visit (select a patient, prepare, at least three blows, repeatability check), shows a live '
     'flow-volume curve, and prints an A4 report. A patient can share results with one doctor by entering a doctor code, and can '
     'unlink, export or delete their data at any time. An administrator approves doctors, manages accounts and settings, and can '
     'review an audit log. The site runs on GitHub Pages with Firebase Authentication and Cloud Firestore. Passwords are held only inside '
     'Firebase Authentication; the application never stores, shows or exports them. Database rules enforce that a patient sees only their '
     'own results, a doctor sees only linked patients, and no one can promote themselves to administrator. We tested these rules with live '
     'accounts, including attempts at privilege escalation, which were rejected. Health data are sensitive personal data, so real use '
     'would also require consent, a retention policy and independent review of the rules.')

doc.add_heading('2.6 What is not proven yet', 2)
para('Versions 1 and 2 were built and tested by our team; the version 3 redesign and the straw-pulp mouthpiece have not yet been. The following limits are therefore important to state clearly:')
for t in [
    'The version 3 housing, electronics layout and web service have been designed and the firmware compiled, but this version has not yet been printed, assembled or measured. The constant K must be calibrated with a 3 L calibration syringe, and accuracy and repeatability must be checked against a reference spirometer.',
    'To stop at the end of a blow, the firmware ends the test when flow stays under 0.25 L/s. A model calculation showed this cuts the slow tail of a healthy blow, so FVC may read about 12% low and the FEV1/FVC ratio may read too high, which could hide mild obstruction. (This came from our own model calculation for version 3 settings.) The firmware now estimates the missing tail, but this correction is unvalidated.',
    'Our acceptance rule requires at least 2 s of blowing, looser than the 6 s in ATS/ERS guidance, and the interpretation uses a fixed FEV1/FVC cut-off of 0.70 with predicted values typed in by the user because we did not include reference equations whose coefficients we could not verify.',
    'No clinical study has been done, and no regulatory approval exists. Spiro is for education and screening only.']:
    p = doc.add_paragraph(t, style='List Bullet'); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
para('Our validation plan is straightforward: calibrate with the 3 L syringe at several flow rates, compare 20 or more volunteers against a '
     'hospital spirometer with consent and teacher/physician supervision, measure the resistance of the pulp mouthpiece, and report '
     'the results whether or not they are favourable.')

doc.add_heading('2.7 Novelty, impact and plan', 2)
para('What is new is the combination, not any single part. Printed venturi spirometers, spirometer mouthpieces made of paper, and straw-pulp '
     'packaging each exist separately; we found no design that links a washable measuring unit, a single-use mouthpiece made from field-burned '
     'residue, and a patient-doctor web service in one low-cost system. The impact is intended on three levels, and each can be checked:')
table([
    ['Level', 'Intended effect', 'How we will check it'],
    ['Health (SDG 3)', 'Early screening of lung function where a clinic spirometer is not available', 'Agreement with a reference spirometer in a supervised comparison'],
    ['Waste and climate (SDG 12, 13)', 'Each mouthpiece is made from residue that would otherwise be burned and can be composted', 'Mass of residue per mouthpiece; compost test of the moulded part'],
    ['Community (SDG 11, 17)', 'Farmers and schools share one loop: straw collection, moulding, screening', 'Pilot with one school and one village health post'],
], [3.6, 6.4, 6.0])
para('Timeline after the summit: weeks 1-4 print, assemble and calibrate version 3 with the 3 L syringe; weeks 5-8 prepare straw-pulp '
     'mouthpiece samples and measure their airflow resistance; weeks 9-12 run a supervised comparison with a reference spirometer and publish '
     'all results, including failures, in the open repository.')

# ---------------------------------------------------------------- Conclusion
doc.add_heading('3. Conclusion', 1)
para('Spiro version 3 joins three ideas that are usually treated separately: a low-cost printed spirometer, an accounts-based service that connects '
     'patients with doctors, and a mouthpiece that turns burned crop residue into a useful, compostable product. The first design '
     'choice - a washable measuring body with a replaceable mouthpiece - makes the third idea possible. If calibration and validation confirm '
     'acceptable accuracy, schools and health posts in smoke-affected areas could screen lungs early, and farming communities would have a '
     'reason to collect straw instead of burning it. If validation fails, the open design, bill of materials and software still allow '
     'other young engineers to find and fix the problem, which is also a way of bridging ideas and youth creativity. Our next steps are '
     'printing and calibration, supplier testing of straw-pulp mouthpieces, and a supervised comparison with a reference spirometer.')

# ---------------------------------------------------------------- References
doc.add_heading('References', 1)
refs = [
 '[1] Mahidol University Repository. Health-damage assessment of crop-residue open burning in Thailand (rice, sugarcane, maize, cassava, oil palm). https://repository.li.mahidol.ac.th/handle/123456789/98397',
 '[2] Thai Environmental Engineering Journal (TCI-Thaijo). Health impacts of rice-straw burning scenarios. https://so05.tci-thaijo.org/index.php/teej/article/download/256260/174186/958025',
 '[3] Graham BL, et al. Standardization of spirometry 2019 update: an official ATS/ERS technical statement. Am J Respir Crit Care Med. 2019;200(8):e70-e88. doi:10.1164/rccm.201908-1590ST',
 '[4] Miller MR, et al. Standardisation of spirometry. Eur Respir J. 2005;26(2):319-338. doi:10.1183/09031936.05.00034805',
 '[5] 3D-printed Venturi spirometer with ESP32. Frontiers in Bioengineering and Biotechnology. 2025. doi:10.3389/fbioe.2025.1664127',
 '[6] Sugar Tech (Springer). Sugar industry by-products in Thailand (bagasse 2016 figure). 2018. https://link.springer.com/10.1007/s12355-018-0599-x',
 '[7] Thaksin University e-book. Sugarcane field residues and open burning in Thailand. https://ebook.tsu.ac.th/store/book/research/full2013_e/full2013_e/assets/basic-html/page13.html',
 '[8] Bangor University. Feasibility of using straw in a strong, thin, pulp moulded packaging material. Industrial Crops and Products. https://research.bangor.ac.uk/portal/en/researchoutputs/feasibility-of-using-straw-in-a-strong-thin-pulp-moulded-packaging-material(d81fbefc-e0b5-45b1-9006-a1bcc9c9c66d)/export.html',
 '[9] Production of molded pulp packaging from rice straw and bagasse coated by chitosan. Burapha Science Journal. https://li05.tci-thaijo.org/index.php/buuscij/article/view/1311',
 '[10] US Patents 5,980,466 and 6,176,833. Biodegradable air tube and spirometer employing same. https://patents.google.com/patent/US6176833',
 '[11] University of Wisconsin-Madison Biomedical Engineering Design. Spirometer final poster (student project, not peer reviewed). https://bmedesign.engr.wisc.edu/public/projects/f09/spirometer/file/view/408e0168-4392-4fac-9b9c-8246935e60cf/Final_Poster_12_3.pdf',
]
for r in refs:
    p = doc.add_paragraph(r); p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.first_line_indent = Cm(-0.8)
    for run in p.runs: run.font.size = Pt(10.5)

# ---------------------------------------------------------------- Attachments
doc.add_heading('Attachments', 1)
para('A. Product page and 3D viewer: https://spiro-medthai.web.app/', indent=False)
para('B. Clinic and patient web application (sign-in): https://spiro-medthai.web.app/login.html', indent=False)
para('C. Open design files (CAD scripts, STL, firmware, bill of materials): https://github.com/TANACHAT007/diy-spirometer', indent=False)
para('Note: figures are CAD renders of the design, not photographs of a built device.', italic=True, indent=False)

out = os.path.join(H, 'IYS7_Health_Spiro_essay.docx')
doc.save(out); print('saved', out)
