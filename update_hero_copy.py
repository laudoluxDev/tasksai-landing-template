#!/usr/bin/env python3
"""Update hero h1 and hero_subhead for all 29 verticals with new messaging."""

import json

HERO_COPY = {
    "contractor": {
        "hero_h1": "Turn Claude into a contractor powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a contractor powerhouse — in under 5 minutes",
        "hero_eyebrow": "For general contractors & construction professionals",
        "hero_subhead": "<strong>180 professionally-built construction workflows for Claude.</strong> Bids, change orders, pay applications, safety plans, and project docs — precision-built for how you actually run a job site.",
    },
    "realtor": {
        "hero_h1": "Turn Claude into a real estate powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a real estate powerhouse — in under 5 minutes",
        "hero_eyebrow": "For real estate agents & brokers",
        "hero_subhead": "<strong>169 professionally-built real estate workflows for Claude.</strong> MLS listings, offer letters, CMAs, buyer emails, and disclosures — precision-built for how you actually close deals.",
    },
    "accounting": {
        "hero_h1": "Turn Claude into an accounting powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into an accounting powerhouse — in under 5 minutes",
        "hero_eyebrow": "For CPAs, bookkeepers & accounting professionals",
        "hero_subhead": "<strong>200 professionally-built accounting workflows for Claude.</strong> Engagement letters, client memos, compliance checklists, and financial reports — precision-built for how you actually practice.",
    },
    "chiropractor": {
        "hero_h1": "Turn Claude into a chiropractic practice powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a chiropractic practice powerhouse — in under 5 minutes",
        "hero_eyebrow": "For chiropractors & chiropractic office staff",
        "hero_subhead": "<strong>200 professionally-built chiropractic workflows for Claude.</strong> SOAP notes, patient communications, insurance documentation, and treatment plans — precision-built for how you actually run your practice.",
    },
    "church": {
        "hero_h1": "Turn Claude into a church admin powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a church admin powerhouse — in under 5 minutes",
        "hero_eyebrow": "For church administrators, pastors & ministry staff",
        "hero_subhead": "<strong>200 professionally-built ministry workflows for Claude.</strong> Bulletins, sermons, member communications, event coordination, and volunteer management — precision-built for how your church actually operates.",
    },
    "dentist": {
        "hero_h1": "Turn Claude into a dental practice powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a dental practice powerhouse — in under 5 minutes",
        "hero_eyebrow": "For dentists & dental office administrators",
        "hero_subhead": "<strong>200 professionally-built dental workflows for Claude.</strong> Patient communications, insurance narratives, treatment plans, and office documentation — precision-built for how you actually run your practice.",
    },
    "designer": {
        "hero_h1": "Turn Claude into a creative powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a creative powerhouse — in under 5 minutes",
        "hero_eyebrow": "For graphic designers, interior designers & creative agencies",
        "hero_subhead": "<strong>200 professionally-built design workflows for Claude.</strong> Client proposals, project briefs, creative briefs, scope documents, and client communications — precision-built for how you actually run a creative practice.",
    },
    "electrician": {
        "hero_h1": "Turn Claude into an electrical contractor powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into an electrical contractor powerhouse — in under 5 minutes",
        "hero_eyebrow": "For electricians & electrical contractors",
        "hero_subhead": "<strong>200 professionally-built electrical contractor workflows for Claude.</strong> Bids, work orders, inspection reports, safety documentation, and client proposals — precision-built for how you actually run jobs.",
    },
    "eventplanner": {
        "hero_h1": "Turn Claude into an event planning powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into an event planning powerhouse — in under 5 minutes",
        "hero_eyebrow": "For event planners, wedding coordinators & corporate event managers",
        "hero_subhead": "<strong>200 professionally-built event planning workflows for Claude.</strong> Event proposals, vendor contracts, run-of-show documents, and client communications — precision-built for how you actually plan events.",
    },
    "farmer": {
        "hero_h1": "Turn Claude into a farm management powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a farm management powerhouse — in under 5 minutes",
        "hero_eyebrow": "For farmers, ranchers & agricultural professionals",
        "hero_subhead": "<strong>200 professionally-built agricultural workflows for Claude.</strong> Crop plans, equipment logs, grant applications, compliance records, and marketing materials — precision-built for how you actually run your operation.",
    },
    "funeral": {
        "hero_h1": "Turn Claude into a funeral home powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a funeral home powerhouse — in under 5 minutes",
        "hero_eyebrow": "For funeral directors, morticians & funeral home staff",
        "hero_subhead": "<strong>200 professionally-built funeral service workflows for Claude.</strong> Obituaries, family communications, service programs, aftercare letters, and compliance documentation — precision-built for how you actually serve families.",
    },
    "hr": {
        "hero_h1": "Turn Claude into an HR powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into an HR powerhouse — in under 5 minutes",
        "hero_eyebrow": "For HR managers, HR generalists & small business owners",
        "hero_subhead": "<strong>200 professionally-built HR workflows for Claude.</strong> Job descriptions, performance reviews, onboarding documents, policy memos, and employee communications — precision-built for how you actually manage people.",
    },
    "insurance": {
        "hero_h1": "Turn Claude into an insurance powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into an insurance powerhouse — in under 5 minutes",
        "hero_eyebrow": "For insurance agents, brokers & claims adjusters",
        "hero_subhead": "<strong>200 professionally-built insurance workflows for Claude.</strong> Coverage summaries, claim narratives, client proposals, follow-up letters, and compliance documentation — precision-built for how you actually work your book.",
    },
    "landlord": {
        "hero_h1": "Turn Claude into a property management powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a property management powerhouse — in under 5 minutes",
        "hero_eyebrow": "For landlords, property managers & rental investors",
        "hero_subhead": "<strong>200 professionally-built property management workflows for Claude.</strong> Lease agreements, tenant notices, maintenance communications, move-in inspections, and eviction documentation — precision-built for how you actually manage properties.",
    },
    "militaryspouse": {
        "hero_h1": "Turn Claude into a military family powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a military family powerhouse — in under 5 minutes",
        "hero_eyebrow": "For military spouses managing businesses & households",
        "hero_subhead": "<strong>200 professionally-built workflows for military spouses.</strong> Business documents, relocation planning, financial organization, resume writing, and household management — precision-built for how you actually keep everything running.",
    },
    "mortgage": {
        "hero_h1": "Turn Claude into a mortgage powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a mortgage powerhouse — in under 5 minutes",
        "hero_eyebrow": "For mortgage loan officers, processors & brokers",
        "hero_subhead": "<strong>200 professionally-built mortgage workflows for Claude.</strong> Pre-approval letters, loan summaries, borrower communications, rate quotes, and compliance documentation — precision-built for how you actually close loans.",
    },
    "mortuary": {
        "hero_h1": "Turn Claude into a mortuary science powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a mortuary science powerhouse — in under 5 minutes",
        "hero_eyebrow": "For morticians, funeral directors & mortuary professionals",
        "hero_subhead": "<strong>200 professionally-built mortuary workflows for Claude.</strong> Family consultation documents, obituaries, service records, aftercare communications, and regulatory paperwork — precision-built for how you actually serve families.",
    },
    "nutritionist": {
        "hero_h1": "Turn Claude into a nutrition practice powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a nutrition practice powerhouse — in under 5 minutes",
        "hero_eyebrow": "For registered dietitians, nutritionists & wellness coaches",
        "hero_subhead": "<strong>200 professionally-built nutrition workflows for Claude.</strong> Meal plans, client assessments, nutrition education materials, progress notes, and practice documentation — precision-built for how you actually work with clients.",
    },
    "pastor": {
        "hero_h1": "Turn Claude into a ministry powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a ministry powerhouse — in under 5 minutes",
        "hero_eyebrow": "For pastors, ministers & church leaders",
        "hero_subhead": "<strong>200 professionally-built ministry workflows for Claude.</strong> Sermon outlines, pastoral letters, counseling notes, congregational communications, and ministry planning documents — precision-built for how you actually lead.",
    },
    "personaltrainer": {
        "hero_h1": "Turn Claude into a fitness business powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a fitness business powerhouse — in under 5 minutes",
        "hero_eyebrow": "For personal trainers, fitness coaches & gym owners",
        "hero_subhead": "<strong>200 professionally-built fitness business workflows for Claude.</strong> Training programs, client assessments, nutrition guidance, progress reports, and marketing content — precision-built for how you actually run your fitness business.",
    },
    "plumber": {
        "hero_h1": "Turn Claude into a plumbing contractor powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a plumbing contractor powerhouse — in under 5 minutes",
        "hero_eyebrow": "For plumbers & plumbing contractors",
        "hero_subhead": "<strong>200 professionally-built plumbing contractor workflows for Claude.</strong> Estimates, work orders, inspection reports, warranty documentation, and customer communications — precision-built for how you actually run jobs.",
    },
    "principal": {
        "hero_h1": "Turn Claude into a school leadership powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a school leadership powerhouse — in under 5 minutes",
        "hero_eyebrow": "For school principals, vice principals & district administrators",
        "hero_subhead": "<strong>200 professionally-built school leadership workflows for Claude.</strong> Parent communications, staff evaluations, policy documents, discipline letters, and improvement plans — precision-built for how you actually lead a school.",
    },
    "restaurant": {
        "hero_h1": "Turn Claude into a restaurant management powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a restaurant management powerhouse — in under 5 minutes",
        "hero_eyebrow": "For restaurant owners, managers & food service operators",
        "hero_subhead": "<strong>200 professionally-built restaurant workflows for Claude.</strong> Staff schedules, vendor communications, menu descriptions, training materials, and customer service responses — precision-built for how you actually run a restaurant.",
    },
    "salon": {
        "hero_h1": "Turn Claude into a salon business powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a salon business powerhouse — in under 5 minutes",
        "hero_eyebrow": "For salon owners, stylists & beauty professionals",
        "hero_subhead": "<strong>200 professionally-built salon business workflows for Claude.</strong> Client consultation notes, service menus, promotional content, staff communications, and client follow-ups — precision-built for how you actually run your salon.",
    },
    "teacher": {
        "hero_h1": "Turn Claude into a teaching powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a teaching powerhouse — in under 5 minutes",
        "hero_eyebrow": "For K-12 teachers, special education staff & school counselors",
        "hero_subhead": "<strong>167 professionally-built teaching workflows for Claude.</strong> Lesson plans, parent communications, IEP support, differentiation strategies, and student assessments — precision-built for how you actually teach.",
    },
    "therapist": {
        "hero_h1": "Turn Claude into a mental health practice powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a mental health practice powerhouse — in under 5 minutes",
        "hero_eyebrow": "For therapists, counselors & mental health professionals",
        "hero_subhead": "<strong>200 professionally-built mental health practice workflows for Claude.</strong> Progress notes, treatment plans, psychoeducation materials, intake documentation, and practice communications — precision-built for how you actually practice.",
    },
    "travelagent": {
        "hero_h1": "Turn Claude into a travel business powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a travel business powerhouse — in under 5 minutes",
        "hero_eyebrow": "For travel agents, travel advisors & tour operators",
        "hero_subhead": "<strong>200 professionally-built travel business workflows for Claude.</strong> Itineraries, client proposals, destination guides, booking confirmations, and travel advisories — precision-built for how you actually serve clients.",
    },
    "vet": {
        "hero_h1": "Turn Claude into a veterinary practice powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a veterinary practice powerhouse — in under 5 minutes",
        "hero_eyebrow": "For veterinarians, vet technicians & veterinary office staff",
        "hero_subhead": "<strong>200 professionally-built veterinary workflows for Claude.</strong> SOAP notes, client discharge instructions, medication guides, practice communications, and patient records — precision-built for how you actually care for patients.",
    },
    "marketing": {
        "hero_h1": "Turn Claude into a marketing powerhouse — in under 5 minutes",
        "hero_h1_no_span": "Turn Claude into a marketing powerhouse — in under 5 minutes",
        "hero_eyebrow": "For marketing managers, digital marketers & creative agencies",
        "hero_subhead": "<strong>206 professionally-built marketing workflows for Claude.</strong> Campaign briefs, social copy, email sequences, competitive analysis, and content strategy — precision-built for how you actually do marketing.",
    },
}

with open('/Users/clio/dev/tasksai-landing-template/verticals.json') as f:
    verticals = json.load(f)

updated = 0
for vert in verticals:
    pid = vert['product_id']
    if pid in HERO_COPY:
        vert.update(HERO_COPY[pid])
        updated += 1
        print(f"  ✅ {pid}: updated")

with open('/Users/clio/dev/tasksai-landing-template/verticals.json', 'w') as f:
    json.dump(verticals, f, indent=2)

print(f"\n✅ Updated {updated} verticals in verticals.json")
