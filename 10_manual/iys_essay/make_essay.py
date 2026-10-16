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
ADVISOR = 'Tanachat Srinurat'

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

para('What makes Spiro different, in three points:', bold=True, after=2)
for t in ['Eco-friendly material: the single-use part is designed to be made from rice straw and cane leaves that are burned in the field today, so waste becomes a product and the smoke that harms lungs is reduced at its source.',
          'Made for the environment and health together: the same fields that cause the lung problem supply the material for screening it, which links air pollution, public health and circular economy in one design.',
          'Affordable and accessible: the whole device is estimated at about 3,100 baht (about USD 85) in parts, uses a standard 3D printer and common electronics, and its open files let a school or health post build it locally.']:
    p = doc.add_paragraph(t, style='List Bullet'); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

# ---------------------------------------------------------------- Body
doc.add_heading('2. Body', 1)
doc.add_heading('2.1 Why this device is needed, and why access and price matter', 2)
para('Chronic obstructive pulmonary disease (COPD) is the third leading cause of death in the world, causing about 3.4 million deaths in 2023, '
     'roughly 6% of all deaths; nearly 90% of COPD deaths under the age of 70 occur in low- and middle-income countries. The World Health '
     'Organization states that COPD should be confirmed with spirometry, and that in low- and middle-income countries spirometry is often not '
     'available, so the diagnosis may be missed [17]. Thailand shows the consequence. A community survey of 1,014 adults in Pathumthani '
     'province using spirometry found COPD in 8.3% and asthma in 10.3%, yet only 9.5% of the people with COPD (8 of 84) and 24.0% of those '
     'with asthma (25 of 104) had ever been diagnosed [18]. In other words, most people with a measurable lung disease did not know they had it. '
     'The reason is mostly access: the test is done where the machine is, and the machine is where the budget is.')
para('This is why price and access are not a side feature but the core of the design. A device that costs a fraction of a clinic spirometer, '
     'that a school or village health post can build and repair itself, and whose results reach a doctor through a phone, moves the first lung test '
     'from the hospital to the community, where the smoke is. Early detection matters because the harm of smoke is cumulative: a farmer or '
     'child who learns early that their airflow is reduced can change exposure, treat asthma, stop smoking and be referred before disability. '
     'The reusable measuring body keeps the price of each test low, and the single-use mouthpiece, made from straw instead of plastic, keeps the '
     'cost per person low and the environmental cost close to zero. Making the device both cheap and green is therefore the same goal seen from '
     'two sides: reach more people without creating more waste or more smoke.')
doc.add_heading('2.2 The problem and the gap', 2)
para('Spirometry is the test used to detect and follow obstructive lung disease; international standards from the American Thoracic '
     'Society and European Respiratory Society (ATS/ERS) define how it should be performed, including at least three acceptable '
     'blows that repeat within 0.15 L [3][4]. Commercial spirometers meet these standards but are designed for clinics. Our goal is '
     'more modest: a device that a school, a community health volunteer or a village health post could build and use for '
     'screening, and that passes results to a doctor. Research groups have already shown that printed venturi spirometers are '
     'feasible; one 2025 study reported about 1.5% error against a 2 L calibration pump for a 3D-printed venturi with an ESP32 [5]. '
     'What is missing in the literature we found is a low-cost design that also deals with infection control and waste, and that is '
     'paired with an accounts-based service connecting patient and doctor.')

doc.add_heading('2.3 Where Spiro comes from: our earlier prototypes', 2)
para('Spiro builds on a platform our team had already made work. Our earlier device, SmartLung, is a respiratory-muscle training '
     'device with a built-in display and sensor that sends its results to a web dashboard so that caregivers and clinicians can monitor '
     'elderly users remotely. It was developed through two prototype versions and won the Gold Award at WICO 2026 (World Invention '
     'Creativity Olympic, 15th edition, Seoul, 16-18 July 2026), a Silver Medal at iCAN 2026 (international invention competition, '
     'online, August 2026) and the OFEED Special Award at iCAN 2026 [16]. These awards were given for SmartLung, a training device, '
     'not for a spirometer. Spiro version 3 uses the same sensing principle and the same kind of remote-monitoring web application as SmartLung, '
     'which our team has already built and demonstrated, and applies them to a new purpose, lung-function screening. '
     'Its new work is concentrated on the part that creates the most waste, the single-use mouthpiece, made from agricultural waste, while '
     'the measuring unit is reused. The rest of this section describes the version 3 design.')
doc.add_heading('2.4 How version 3 works', 2)
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

doc.add_heading('2.5 From burned fields to the mouthpiece', 2)
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
para('Plant fibre is not new to medicine, which supports the safety direction of our choice. Cellulose, the main component of straw and bagasse, '
     'is widely studied and used as a biocompatible, biodegradable material for wound dressings [19][20], and cellulose nanocrystals made from sugarcane bagasse '
     'have been formed into wound-dressing films in a peer-reviewed study [21]. Single-use moulded-pulp products are also an established class of '
     'hospital disposables: manufacturers sell moulded-fibre bedpans and liners, and a British standard (PAS 29) covers disposable pulp products for '
     'healthcare [22]. These examples concern purified cellulose or recycled-paper pulp, not rice-straw mouthpieces in a breathing circuit, so they show '
     'that the material family is accepted in healthcare, not that our part is already approved.')
para('Two honest cautions apply. First, a mouthpiece is not a bacterial filter, so single-person use and hygiene rules still matter. '
     'Second, we found no peer-reviewed measurement of airflow resistance or accuracy for crop-residue pulp mouthpieces in a spirometer; '
     'the studies above support the material, not the medical use. That measurement is part of our plan.')

doc.add_heading('2.6 An online system for patients, doctors and administrators', 2)
para('Data are only useful if the right person can see them. We built a web service with three roles. A patient registers, blows into the '
     'device or follows the on-screen coaching, and sees a history and trend. A doctor, after approval by an administrator, '
     'uses a clinic mode that guides a visit (select a patient, prepare, at least three blows, repeatability check), shows a live '
     'flow-volume curve, and prints an A4 report. A patient can share results with one doctor by entering a doctor code, and can '
     'unlink, export or delete their data at any time. An administrator approves doctors, manages accounts and settings, and can '
     'review an audit log. The site is hosted on Firebase Hosting with Firebase Authentication and Cloud Firestore. Passwords are held only inside '
     'Firebase Authentication; the application never stores, shows or exports them. Database rules enforce that a patient sees only their '
     'own results, a doctor sees only linked patients, and no one can promote themselves to administrator. We tested these rules with live '
     'accounts, including attempts at privilege escalation, which were rejected. Health data are sensitive personal data, so real use '
     'would also require consent, a retention policy and independent review of the rules.')

doc.add_heading('2.7 Validation plan and known limits', 2)
para('The SmartLung prototypes were built and demonstrated by our team; the Spiro version 3 spirometer design and the straw-pulp mouthpiece have not yet been. Because we want the numbers to be trusted, we state the remaining limits openly and show how each will be closed:')
for t in [
    'The version 3 housing, electronics layout and web service have been designed and the firmware compiled, but this version has not yet been printed, assembled or measured. The constant K must be calibrated with a 3 L calibration syringe, and accuracy and repeatability must be checked against a reference spirometer.',
    'To stop at the end of a blow, the firmware ends the test when flow stays under 0.25 L/s. A model calculation showed this cuts the slow tail of a healthy blow, so FVC may read about 12% low and the FEV1/FVC ratio may read too high, which could hide mild obstruction. (This came from our own model calculation for version 3 settings.) The firmware now estimates the missing tail, but this correction is unvalidated.',
    'Our acceptance rule requires at least 2 s of blowing, looser than the 6 s in ATS/ERS guidance, and the interpretation uses a fixed FEV1/FVC cut-off of 0.70 with predicted values typed in by the user because we did not include reference equations whose coefficients we could not verify.',
    'No clinical study has been done, and no regulatory approval exists. Spiro is for education and screening only.']:
    p = doc.add_paragraph(t, style='List Bullet'); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
para('Our validation plan is straightforward: calibrate with the 3 L syringe at several flow rates, compare 20 or more volunteers against a '
     'hospital spirometer with consent and teacher/physician supervision, measure the resistance of the pulp mouthpiece, and report '
     'the results whether or not they are favourable.')

doc.add_heading('2.8 Why we believe it will work: evidence and risk plan', 2)
para('A design is credible if its riskiest assumptions are supported by independent evidence and each remaining risk has a way to be closed. '
     'We list the three riskiest assumptions below.')
table([
    ['Assumption', 'Supporting evidence found', 'Open risk and how we close it'],
    ['A printed venturi with a differential-pressure sensor can measure FVC and FEV1 accurately enough for screening',
     'A 3D-printed venturi with ESP32 reported about 1.5% error against a 2 L pump [5]. A venturi home spirometer on 8 healthy adults reported r = 0.992 (FVC) and 0.968 (FEV1) against standard equipment [12]. A frugal printed venturi on 30 participants reported ICC 0.97 for FEV1 against a CE-marked spirometer, but peak flow was less accurate (mean error 18%) [13].',
     'Our own K constant and end-of-blow rule are unvalidated. Close with 3 L syringe calibration, then a supervised comparison with a reference spirometer in a hospital. Peak flow will be reported with a caution until proven.'],
    ['A moulded rice-straw pulp mouthpiece can be made strong and moisture-tolerant',
     'Straw trays with up to 80% straw were stronger in tension than polystyrene and lost about 20% of mass in 4 weeks in soil [8]. In a Thai study, a chitosan coating lowered water absorption of rice-straw packaging from 27% to 4% [9]. A fluorine-free chitosan coating on moulded-pulp boxes gave a water contact angle of about 115 degrees [14].',
     'No study measured this material inside a spirometer. Close by moulding samples, weighing and wetting them, and measuring airflow resistance and leak against a standard cardboard mouthpiece. The fallback is a standard cardboard mouthpiece.'],
    ['A single-use mouthpiece is enough for infection control',
     'Hospital guidance recommends a single-use in-line bacterial/viral filter for spirometry [15]. Cardboard mouthpieces alone are described in patent literature as an older practice [10].',
     'We will not claim the straw mouthpiece is a filter. In a hospital pilot it is used together with a standard disposable filter on the reusable side, and cleaning follows the hospital protocol.'],
], [3.8, 6.4, 5.8], size=9.5)
para('How confident are we? We do not quote a percentage chance of success, because an invented number would be less honest than a graded one. '
     'Our reading of the evidence is: HIGH for the measuring principle (several independent printed-venturi studies), MEDIUM for moulding a '
     'usable mouthpiece from straw (the material is proven, the shape and wet strength are not), and LOW-TO-MEDIUM for clinical-grade infection '
     'control without a filter, which is why a filter is part of the plan. A mouthpiece touches the lips and mouth for a few minutes, so we expect it to be '
     'assessed under the ISO 10993-1 biocompatibility framework for mucosal-contact devices; this must be confirmed with the regulator before any '
     'patient use, and no pulp-specific ISO 10993 data for rice straw were found.')
doc.add_heading('2.9 Affordable and accessible by design', 2)
para('Access is a design goal, not an afterthought. The bill of materials lists 26 items totalling about 3,084 baht at estimated prices '
     '(a design estimate from online marketplace prices, not receipts). The measuring unit is printed in about 27 hours on a hobby-class '
     'printer using about 0.5 kg of filament, and nothing in it needs a special factory process. The part that is consumed - the mouthpiece - '
     'costs about 5 baht in printed form for the prototype, and the proposal is to replace it with moulded residue pulp, a material that is '
     'locally available and nearly free at the source. Because the design, firmware, web service and assembly instructions are published openly, a school or '
     'health post can build, repair and extend the device without buying a licence. We have not benchmarked the price of commercial '
     'spirometers in this essay, and a low price is meaningful only if accuracy is proven, which is why our validation plan comes first.')
doc.add_heading('2.10 Novelty, impact and plan', 2)
para('What is new is the combination, not any single part. Printed venturi spirometers, spirometer mouthpieces made of paper, and straw-pulp '
     'packaging each exist separately; we found no design that links a washable measuring unit, a single-use mouthpiece made from field-burned '
     'residue, and a patient-doctor web service in one low-cost system. The impact is intended on three levels, and each can be checked:')
table([
    ['Level', 'Intended effect', 'How we will check it'],
    ['Health (SDG 3)', 'Early screening of lung function where a clinic spirometer is not available', 'Agreement with a reference spirometer in a supervised comparison'],
    ['Waste and climate (SDG 12, 13)', 'Each mouthpiece is made from residue that would otherwise be burned and can be composted', 'Mass of residue per mouthpiece; compost test of the moulded part'],
    ['Community (SDG 11, 17)', 'Farmers and schools share one loop: straw collection, moulding, screening', 'Pilot with one school and one village health post'],
], [3.6, 6.4, 6.0])
para('The path to the hospital is deliberately staged. Stage 1 (weeks 1-4): print, assemble and calibrate version 3 with the 3 L syringe, '
     'and publish the error. Stage 2 (weeks 5-8): mould straw-pulp mouthpiece samples and measure their strength when wet, leak and airflow '
     'resistance against a standard cardboard mouthpiece. Stage 3 (weeks 9-12 and after): apply for ethics approval with a hospital '
     'partner and a physician supervisor, then run a supervised comparison with the hospital reference spirometer on volunteers who '
     'give informed consent, using an in-line disposable filter. No patient will use the device before Stages 1 and 2 are passed and '
     'ethics approval is granted. All results, including failures, will be published in the open repository.')

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
 '[12] Design and evaluation of a novel Venturi-based spirometer for home respiratory monitoring. Sensors. 2024. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11398045/',
 '[13] A frugal Arduino-based spirometer for low-resource settings: design, development and validation of a preliminary prototype. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12816365/',
 '[14] Sustainable water- and oil-repellent coating for disposable meal boxes based on highly deacetylated chitosan. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12195517/',
 '[15] NHS BSW Integrated Care Board. Infection prevention and control best practice guidance for spirometry. 2022. https://bsw.icb.nhs.uk/wp-content/uploads/sites/6/2022/06/Bath-North-East-Somerset-Swindon-and-Wiltshire-BSW-Infection-Prevention-and-Control-Best-Practice-guidance-for-Spirometry-2022.pdf',
 '[16] SmartLung project and award page (team portfolio, with certificates and photos). https://tanachat007.github.io/poom-portfolio/smartlung.html',
 '[17] World Health Organization. Chronic obstructive pulmonary disease (COPD) fact sheet. https://www.who.int/news-room/fact-sheets/detail/chronic-obstructive-pulmonary-disease-(copd)',
 '[18] Prevalence of chronic obstructive pulmonary disease and asthma in the community of Pathumthani, Thailand. Diseases (MDPI). 2025;13(5):130. https://pmc.ncbi.nlm.nih.gov/articles/PMC12109837/',
 '[19] An overview of cellulose derivatives-based dressings for wound-healing management. Pharmaceuticals. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8706040/',
 '[20] Cellulose-based biomaterials for wound healing (clinically oriented review). Applied Sciences. 2021;11(17):7769. https://www.mdpi.com/2076-3417/11/17/7769',
 '[21] Sugarcane bagasse-derived cellulose nanocrystal / polyvinyl alcohol / gum tragacanth composite film for wound dressing. Int J Biomaterials. 2023. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10359141/',
 '[22] Vernacare / Ebos Healthcare product listings for single-use moulded-pulp bedpans and liners citing PAS 29:1999 (manufacturer information, not independent evidence). https://www.eboshealthcare.com.au/catalogue-products/infection-prevention--control/bedpans--urinals/liner/bedpan-liners-75s/',
]
for r in refs:
    p = doc.add_paragraph(r); p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.first_line_indent = Cm(-0.8)
    for run in p.runs: run.font.size = Pt(10.5)

# ---------------------------------------------------------------- Attachments
doc.add_heading('Attachments', 1)
para('A. Product page and 3D viewer: https://medthai-spirometer.web.app/', indent=False)
para('B. Clinic and patient web application (sign-in): https://medthai-spirometer.web.app/login.html', indent=False)
para('C. Earlier project SmartLung and its award certificates: https://tanachat007.github.io/poom-portfolio/smartlung.html', indent=False)
para('D. Open design files (CAD scripts, STL, firmware, bill of materials): https://github.com/TANACHAT007/diy-spirometer', indent=False)
para('Note: figures are CAD renders of the design, not photographs of a built device.', italic=True, indent=False)

out = os.path.join(H, 'IYS7_Health_Spiro_essay.docx')
doc.save(out); print('saved', out)
