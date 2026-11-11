#!/usr/bin/env python3
"""Create HTML/PDF using the visual style of the supplied CV.

This is an MVP reference renderer, not a completed Resume Studio.
Input: JSON import from career_kb_seed.json (can be extended with revised CV facts).
Options: --json ... --html ... --pdf ...
Dependencies for PDF: pip install playwright; Chromium installed or `playwright install chromium`.
"""
from __future__ import annotations
import argparse, html, json, pathlib, shutil
from datetime import datetime

HERE=pathlib.Path(__file__).resolve().parent
CSS=HERE/'resume_template.css'

def h(value): return html.escape('' if value is None else str(value), quote=True)
def visible(value): return value['value'] if isinstance(value,dict) and 'value' in value else value
MONTHS={1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}
def date_txt(iso):
    if not iso: return 'Atualmente'
    year,month=map(int,iso.split('-')[:2]); return f'{MONTHS[month]} {year}'

def list_html(items,css_class='side-list'):
    return '<ul class="'+h(css_class)+'">'+''.join('<li>'+h(x)+'</li>' for x in items)+'</ul>'

def exp_html(e,statements):
    bullets=[statements[id]['text_original'] for id in e.get('responsibility_statement_ids',[]) if id in statements]
    loc=e.get('location')
    loc_text=(' | '+', '.join(x for x in (loc.get('city'),loc.get('country')) if x)) if loc else ''
    return '''<article class="entry"><div class="entry-date"><span>{start}</span><span>{end}</span></div>
      <div class="entry-body"><h3 class="entry-role">{title}</h3>
      <p class="entry-org">{company}<span class="location">{location}</span></p>
      {bullets}</div></article>'''.format(start=h(date_txt(e['start_date'])),end=h(date_txt(e.get('end_date'))), title=h(e['job_title_original']),company=h(e['company_name_original']),location=h(loc_text),bullets=list_html(bullets,'entry-bullets'))

def edu_html(e):
    loc=e.get('location')
    loc_text=(' | '+', '.join(x for x in (loc.get('city'),loc.get('country')) if x)) if loc else ''
    end=e.get('end_date_original') if not e.get('end_date') else date_txt(e['end_date'])
    return '''<article class="entry"><div class="entry-date"><span>{start}</span><span>{end}</span></div>
    <div class="entry-body"><h3 class="entry-role">{program}</h3>
      <p class="entry-org">{institution}<span class="location">{location}</span></p>
      {detail}</div></article>'''.format(start=h(date_txt(e['start_date'])),end=h(end),program=h(e['program_original']),institution=h(e['institution']),location=h(loc_text),detail=('<p class="detail">'+h(e['description_original'])+'</p>') if e.get('description_original') else '')

def document(data):
    profile=data['profile']
    stmt={s['id']:s for s in data.get('statements',[])}
    sidebar=[s['original_labels'][0] for s in data['skills'] if s.get('explicitly_listed_in_skills_section')]
    # Recover the exact order in the reference PDF.
    order=['Javascript','Typescript','React.Js','Next.Js','Git','Redux','Rest API','GraphQL','Desenvolvimento Ágil','Testes unitários']
    sidebar=sorted(sidebar,key=lambda s:order.index(s) if s in order else len(order))
    langs=[l['language']+' | '+l['proficiency_original'] for l in data.get('languages',[])]
    icon_mail='<svg viewBox="0 0 14 14" aria-hidden="true"><rect x="1.3" y="3" width="11.4" height="8" rx="1"/><path d="M1.6 4l5.4 4 5.4-4"/></svg>'
    icon_phone='<svg viewBox="0 0 14 14" aria-hidden="true"><rect x="3.4" y="1" width="7.2" height="12" rx="1.4"/><path d="M5.5 11.4h3"/></svg>'
    return '''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/><title>Currículo - {name}</title>
    <style>{stylesheet}</style></head><body>
    <div class="paper"><div class="right-background"></div><div class="timeline-line"></div>
    <aside class="sidebar"><div class="side-inner"><div class="contact-block">
      <div class="contact-row">{icon_mail}<span>{email}</span></div>
      <div class="contact-row">{icon_phone}<span>{phone}</span></div></div>
      <section class="side-section objective"><h2>OBJETIVO</h2><p>{objective}</p></section>
      <section class="side-section skills"><h2>HABILIDADES</h2>{skills}</section>
      <section class="side-section languages"><h2>IDIOMAS</h2>{langs}</section></div></aside>
    <main class="page-content"><header class="resume-header"><h1>{name}</h1>
      <div class="subtitle">{headline}</div></header>
      <section class="experiences"><h2 class="section-header">EXPERIÊNCIA</h2>{experiences}</section>
      <section class="education"><h2 class="section-header">EDUCAÇÃO</h2>{education}</section>
    </main></div></body></html>'''.format(name=h(visible(profile['full_name'])),headline=h(visible(profile['professional_headline'])),email=h(visible(profile['email'])),phone=h(visible(profile['phone_original'])), objective=h(visible(profile['objective_original'])),skills=list_html(sidebar),langs=list_html(langs),experiences=''.join(exp_html(e,stmt) for e in data.get('experiences',[])),education=''.join(edu_html(e) for e in data.get('education',[])),icon_mail=icon_mail,icon_phone=icon_phone,stylesheet=CSS.read_text(encoding="utf-8"))

def render_pdf(html_path,pdf_path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=shutil.which('chromium') or shutil.which('google-chrome'), headless=True, args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1200,'height':1600},device_scale_factor=1)
        page.set_content(html_path.read_text(encoding='utf-8'), wait_until='load')
        page.emulate_media(media='print')
        page.pdf(path=str(pdf_path),prefer_css_page_size=True,print_background=True,display_header_footer=False)
        print('HTML measures',page.locator('.page-content').evaluate('(el) => ({height:el.getBoundingClientRect().height,top:el.getBoundingClientRect().top})'))
        browser.close()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',default=str(HERE/'career_kb_seed.json')); ap.add_argument('--html',default=str(HERE/'curriculo_template_recriado.html')); ap.add_argument('--pdf',default=str(HERE/'curriculo_template_recriado.pdf')); ap.add_argument('--no-pdf',action='store_true');args=ap.parse_args()
    data=json.loads(pathlib.Path(args.json).read_text(encoding='utf-8'))
    html_path=pathlib.Path(args.html).resolve(); html_path.write_text(document(data),encoding='utf-8')
    if not args.no_pdf:render_pdf(html_path,pathlib.Path(args.pdf).resolve())
    print('Generated',html_path)
if __name__=='__main__':main()
