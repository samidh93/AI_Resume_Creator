import openai
import json 
import yaml
from pathlib import Path
from pydantic import BaseModel
from resume_parser import ResumeParser
from job_description_interface import JobDescriptionInterface
from resume_parser import ResumeParser
import re
from ai_interface import AIInterface

class ATSResult(BaseModel):
    ats_score: int
    #matched_skills: list[str]
    missing_skills: list[dict]
    suggested_improvements: str

class JobSkills(BaseModel):
    required_skills: list[dict]  # Renaming 'skills' to match the model's response

class ResumeAnalyzer:
    def __init__(self,  job_description:str, resume:ResumeParser):
        #openai.api_key = api_key
        # Create the AI interface
        self.model = AIInterface(
                model_provider="ollama",
                model_name= "qwen2.5:3b", #"llama3.2:latest",              
                temperature=0,
                #max_tokens=100,
                format="json"
            )
        self.matched_skills = []
        self.missing_skills = []
        self.suggested_improvements = ""
        self.job_description_text = re.sub(r'\s+', ' ', job_description).strip()
        self.resume_text = resume.get_required_fields_for_ats()
        self.job_required_skills = self.get_job_required_skills()

    def get_job_required_skills(self):
        """use AI to extradct required skills from job description"""
        prompt = f"""
        extract required skills from job description:
        {self.job_description_text}
        Return **only** a **JSON object** with the following **exact** structure:
        ```json
        {{
            "required_skills": [
                {{"category": "Programming Languages", "name": "Python", "level": "Advanced"}},  
                ...
            ], 
        }}
        ```
        """
        response_content = self.model.get_completion(prompt=prompt)
        print("response_content: ", response_content)
        return JobSkills(**json.loads(response_content))
    

    def compare(self) -> ATSResult:
        """Calculate the ATS score for the resume based on the job description."""
        system_prompt = f"""
        You are an Applicant Tracking System (ATS) that evaluates resumes against job descriptions.
        Return **only** a **JSON object** with the following **exact** structure:
        ```json
        {{
            "ats_score": <numeric_value_between_0_and_100>,
            "missing_skills": [
                {{"category": "Programming Languages", "name": "Python", "level": "Advanced"}},  
                ...
            ], 
            "suggested_improvements": "Detailed suggestions on how to improve the resume."
        }}
        ```
        """
        user_prompt = f"""
        **Job Description:**
        {self.job_required_skills}
        **Resume:**
        {self.resume_text}
        """        
        print("user_prompt: ", user_prompt)
        #response = openai.chat.completions.create(
        #    model="gpt-4o-mini",
        #    response_format={"type": "json_object"},
        #    temperature=0,  # Ensures consistent results
        #    messages=[
        #        {"role": "system", "content": "You are an ATS expert evaluating resumes for compatibility."},
        #        {"role": "user", "content": prompt}
        #    ]
        #)
        #response_content = response.choices[0].message.content
        messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        response_content = self.model.get_completion(messages)
        print("response_content: ", response_content)
        return ATSResult(**json.loads(response_content))


if __name__ == "__main__":
    secrets_path = Path('input/secrets.yaml')
    #secrets = yaml.safe_load(open(secrets_path, 'r'))
    #api_key = secrets['api_key']
    resume = ResumeParser("input/sami_dhiab_resume.yaml")
    job_desc = """"
Senior Data Engineer (m/w/d)
Publication Date:  Mar 17, 2025
Ref. No:  529029
Location:  Düsseldorf, DE Dusseldorf, DE München, DE Berlin, DE Hamburg, DE Frankfurt, DE Essen, DE Fürth, DE Stuttgart, DE
Unsere Werte:
#GrowTogether- Wir pflegen eine integrative und gerechte Gemeinschaft und schmieden langfristige und vertrauensvolle Beziehungen zueinander.
#DareToTry – Wir wissen, wann es an der Zeit ist für gewollten Fortschritt ein Risiko einzugehen.
#DoTheRightThing – Wir handeln nachhaltig und verbessern dadurch das Wohl von Menschen und unserem Planeten.
#StayCurious – Wir sind neugierig und heben dadurch unsere Ergebnisse auf eine neue Stufe.
Wir suchen neue Kolleg:innen an unseren bundesweiten Standorten.
Das sind Ihre Aufgaben:
Im Rahmen von Pre-Sales Aktivitäten qualifizieren Sie Ausschreibungen aus technischer Sicht, analysieren Kundenanforderungen, prüfen die Machbarkeit und unterstützen bei der Erstellung von Angeboten in Bezug auf Standardelemente mit erweiterter Komplexität.
Sie unterstützen bei der Akquise neuer Projekte, leiten Workshops und identifizieren proaktiv Optimierungs- und Geschäftsmöglichkeiten im laufenden Projekt. Zudem wirken Sie an anschließenden Vertriebsaktivitäten mit.
Sie kommunizieren auf Fachbereichsebene der Kundenseite.
Sie leiten Teilprojekte und halten Aufwände gemäß (Projekt-) Vorgaben in einem Aufgabenbereich ein.
Im Projekt arbeiten Sie an der Umsetzung von Lösungskomponenten oder Funktionsbausteinen von Data-Analytics-Architekturen.
Sie wirken bei Konzeption, Design, Implementierung, Test und Beratung mit und unterstützen bei der Umsetzung von Lösungskomponenten oder Funktionsbausteinen. Was sind unsere Tätigkeitsfelder:
Sie arbeiten in Projekten vorwiegend mit Python (z. B. pandas, numpy) und SQL, Jupyter, PySpark, Databricks,.... Zudem beschäftigen Sie sich mit Spark, Data Warehousing, Data Engineering, Big Data und MLOps.
Sie arbeiten mit den modernsten Cloud-Technologien (AWS, Azure oder GCP).
Sie vertreten unser Unternehmen überzeugend nach außen und arbeiten mit den unterschiedlichsten Branchen zusammen.
Wir arbeiten sowohl mit strukturierten als auch mit unstrukturierten Daten (Online- und Offline-Daten wie z.B. Zahlungstransaktionen, Call-Center Anrufe usw.) und helfen unseren Kunden dabei, ihre Daten richtig zu verstehen
Projektteams bestehen in der Regel aus 2 - 5 Personen (Analysten, Engineers, DataScientists, Project Manager), die sowohl an langfristigen Projekten als auch an kürzeren "Piloten" arbeiten
Das Ergebnis Ihrer Arbeit optimiert geschäftskritische Funktionen bei unseren Kunden und hat einen direkten Einfluss auf deren wirtschaftlichen Erfolg
Wir nutzen beispielsweise prädiktive Modelle, um die Welt der Online-Kommunikation zu verbessern, überwachen die Qualität der Regalplatzierung mit modernster Computer Vision und arbeiten an der Betrugserkennung
Das bringen Sie mit:
Bachelor oder vergleichbar
Langjährige Berufserfahrung (mind. 5 Jahre in dem Umfeld)
Sehr gute Kenntnisse der MS Office Produkte Excel, Word, PowerPoint, etc.
Sehr gute Kommunikationsfähigkeiten mindestens in Deutsch und Englisch
Teamfähigkeit, unternehmerisches Denken, Selbständigkeit und Motivation runden Ihr Profil ab
Spaß am Arbeiten im Team und an der eigenständigen Erarbeitung neuer Themen.
Das bieten wir Ihnen:
Freiheit und Autonomie - Sie haben die Chance, an Produkten, Projekten und Services mitzuwirken, die die Welt verändern. Moderne, agile Arbeitsformen zusammen mit unseren Kunden begleiten Sie im Alltag.
Innovation und Wachstum – Sie haben die Möglichkeit, in einem innovativen Umfeld etwas aufzubauen und zu bewegen, kontinuierlich zu lernen, Sich weiterzuentwickeln. Hierbei werden Sie durch ein nationales und internationales Mitarbeiternetzwerk unterstützt.
Vertrauen und Fürsorge - Wir fördern jede:n Einzelne:n und jedes Team, denn gemeinsam sind wir klüger, erfolgreicher und haben mehr Spaß an unserer Arbeit.
Gesundheit und Nachhaltigkeit - Bei uns steht Ihr Wohlbefinden an erster Stelle! Genießen Sie flexible Arbeitszeiten, 30 Tage bezahlten Jahresurlaub, die Möglichkeit, mobil zu arbeiten und noch vieles mehr. Unsere Inklusionsvereinbarung sorgt für ein barrierefreies Arbeitsumfeld, das Menschen mit Behinderungen unterstützt. Nachhaltigkeit ist ein zentraler Bestandteil unserer Kundenlösungen und unseres eigenen Handelns.
Vergütung und Sozialleistungen - Wir wissen, dass unsere Mitarbeiter:innen unsere treibende Kraft sind. Deshalb bieten wir Ihnen ein attraktives Gehalt und zusätzliche Sozialleistungen, die Ihren Bedürfnissen und Ihrer Lebensweise entsprechen. Weitere Vorteile warten auf Sie!
Ihre Ansprechpartnerin:
Bei Fragen zu diesem Stellenangebot wenden Sie Sich bitte an Frau Siana Dimitrova über Siana Dimitrova | LinkedIn.
Bevorzugte Bewerbungsform:
Haben wir Ihr Interesse geweckt? Dann nutzen Sie bitte den Button „Apply now“ und bewerben Sie Sich schnell und einfach online.
Das sind wir:
Die science + computing AG, ein Unternehmen von Eviden, erbringt hochwertige, innovative und spezialisierte IT-Dienstleistungen für anspruchsvolle internationale Kunden im Bereich Automotive und Manufacturing. Mit 350 hochqualifizierten Mitarbeitenden in Deutschland und Rumänien stellen wir sicher, dass unsere Kunden ihre Geschäftsziele im Bereich R&D und Engineering, sowie beim Betrieb ihrer geschäftskritischen Anwendungen bestmöglich realisieren können.
Eviden  ist ein Technologieführer der nächsten Generation im Bereich der datengesteuerten, vertrauenswürdigen und nachhaltigen digitalen Transformation mit einem starken Portfolio an patentierten Technologien. Mit weltweit führenden Positionen in den Bereichen Advanced Computing, Security, KI, Cloud und digitale Plattformen bringt Eviden ein fundiertes Fachwissen für alle Branchen in über 47 Ländern mit. Mit 41.000 Talenten von Weltklasse erweitert Eviden die Möglichkeiten im Umgang mit Daten und Technologien über das gesamte digitale Kontinuum, heute und für kommende Generationen. Eviden ist ein Unternehmen der Atos-Gruppe mit einem Jahresumsatz von ca. 5 Milliarden Euro.
Wir freuen uns auf Sie!
Als eines der Top 20 Unternehmen, die für den Inklusionspreis der Wirtschaft nominiert wurden, freuen wir uns über Ihre Bewerbung, unabhängig von Herkunft, Religion, Farbe, Geschlecht, Alter, Behinderung oder sexueller Orientierung. Alle Entscheidungen während des gesamten Rekrutierungsprozesses beruhen ausschließlich auf den Qualifikationen, Fähigkeiten, Kenntnissen und Erfahrungen sowie relevanten Geschäftsanforderungen.
Wir legen Wert auf Chancengleichheit und freuen uns über Bewerbungen von Menschen mit Behinderung. Bei gleicher Qualifikation werden schwerbehinderte Bewerber:innen und diesen gleichgestellten Menschen bevorzugt berücksichtigt.
    """
    ra = ResumeAnalyzer( job_desc, resume)
    ats_result = ra.compare()
    print(f"ATS Score: {ats_result.ats_score}")
    #print(f"Matched Skills: {ats_result.matched_skills}")
    print(f"Missing Skills: {ats_result.missing_skills}")
    print(f"Suggested Improvements: {ats_result.suggested_improvements}")
