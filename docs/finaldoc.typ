// main.typ

#import "finaldoc_template.typ": (
  abstract-page, acknowledgements, certificate, checklist, contents-placeholder, cover-page, evaluation-sheet, project,
  title-page,
)

// ── DOCUMENT VARIABLES ────────────────────────────────────────────────
#let projectTitle = "Shared Media Streaming Platform"
#let studentName = "Vaisakh K M"
#let studentID = "202117B3543"
#let studentEmail = "202117B3543@wilp.bitspilani.ac.in"
#let mentorName = "Harpreet Kaur"
#let mentorEmail = "harpreet.kaur@hcltech.com"
#let mentorTitle = "Project Manager"
#let mentorOrg = "HCLTech, Canada"
#let submissionDate = "January 2026"
#let completionDate = "26/01/2026"
#let workLocation = "HCLTech, Nagpur"

// ── DOCUMENT ───────────────────────────────────────────────────────────
#show: project

#cover-page(
  projectTitle,
  studentName,
  studentID,
  workLocation,
  submissionDate,
)

#title-page(
  projectTitle,
  studentName,
  studentID,
  workLocation,
  mentorName,
  mentorTitle,
  mentorOrg,
  submissionDate,
)

#certificate(
  projectTitle,
  studentName,
  studentID,
  mentorName,
  mentorTitle,
  mentorOrg,
  completionDate,
)

#abstract-page(
  projectTitle,
  studentName,
  studentID,
  studentEmail,
  workLocation,
  mentorName,
  mentorOrg,
  mentorEmail,
  completionDate,
)

#evaluation-sheet(
  projectTitle,
  studentName,
  studentID,
  studentEmail,
  workLocation,
  mentorName,
  mentorOrg,
  mentorEmail,
)

#contents-placeholder()

#acknowledgements()





#checklist()
