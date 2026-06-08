from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from generate_class12_commerce_practice import dataset, make_topic


ROOT = Path(__file__).resolve().parents[1]
BOOK = "Accountancy Syllabus Question Bank 2025-26"
PDF_PATH = r"C:\Users\acer\Downloads\Accountancy_SrSec_2025-26.pdf"
SYLLABUS_URL = "https://cbseacademic.nic.in/web_material/CurriculumMain26/SrSec/Accountancy_SrSec_2025-26.pdf"


def topic(title: str, easy: str, moderate: str, case: str, points: list[str], distractors: list[str], phrases: list[str] | None = None) -> dict[str, Any]:
    return make_topic(title, easy, moderate, case, points, distractors, phrases)


CHAPTERS: list[dict[str, Any]] = [
    {
        "slug": "fundamentals-of-partnership-and-goodwill",
        "chapterNumber": 1,
        "chapter": "Fundamentals of Partnership and Goodwill",
        "unit": "Unit 1: Accounting for Partnership Firms",
        "topics": [
            topic("partnership deed and act provisions", "State the features of partnership and the role of partnership deed.", "Apply Partnership Act provisions when the deed is silent.", "A firm has no deed clause for interest on capital, salary or profit sharing.", ["Partnership is an agreement among persons to share profits of a business carried on by all or any one acting for all.", "A partnership deed records agreed terms such as ratio, capital, interest, salary and drawings.", "In absence of deed, Partnership Act provisions apply.", "Profits and losses are shared equally when no ratio is agreed.", "No partner is entitled to salary or interest on capital unless agreed."], ["Interest on capital is always allowed without deed.", "Losses are shared by capital ratio when deed is absent.", "A deed is only needed for companies."], ["partnership deed", "Partnership Act 1932", "equal profit sharing", "no salary without agreement", "mutual agency"]),
            topic("fixed and fluctuating capital", "Differentiate fixed and fluctuating capital accounts.", "Prepare the treatment logic for partner adjustments under fixed capital.", "Interest on capital, drawings and profit share must be posted for a fixed-capital firm.", ["Under fixed capital, capital account normally remains unchanged.", "Adjustments such as interest, salary, drawings and profit share are recorded in current accounts.", "Under fluctuating capital, all adjustments are recorded directly in capital accounts.", "Current accounts may show debit or credit balances.", "The method should be identified before preparing partner accounts."], ["Fixed capital changes after every drawing.", "Current account is never prepared under fixed capital.", "Fluctuating capital excludes profit share."], ["fixed capital", "fluctuating capital", "current account", "partner adjustments", "capital balance"]),
            topic("profit and loss appropriation account", "Prepare the order of items in a Profit and Loss Appropriation Account.", "Calculate residual profit after appropriations and distribute it in the profit ratio.", "A firm allows interest on capital, partner salary and guarantee of profit.", ["Profit and Loss Appropriation Account begins with net profit transferred from Profit and Loss Account.", "Interest on capital and partner salary are appropriations of profit if allowed by deed.", "Interest on drawings is credited to the appropriation account.", "Residual profit is divided among partners in the profit sharing ratio.", "Guarantee adjustment is made after computing normal share."], ["Partner loan interest is an appropriation of profit.", "Residual profit is always divided equally.", "Guarantee is ignored if normal profit is lower."], ["net profit", "appropriation", "interest on capital", "interest on drawings", "profit sharing ratio", "guarantee"]),
            topic("goodwill valuation methods", "Name the methods of goodwill valuation in partnership.", "Compare average profit, super profit and capitalization methods.", "A firm must value goodwill before a change in constitution.", ["Goodwill is the value of reputation and expected earning capacity of a firm.", "Average profit method values goodwill by multiplying average profit by years' purchase.", "Super profit method uses excess profit over normal profit.", "Capitalization methods infer goodwill from capitalised value and actual capital.", "Goodwill is adjusted through partners' capital or current accounts as per syllabus treatment."], ["Goodwill is a tangible asset like furniture.", "Super profit means total profit.", "Capitalization method ignores normal rate of return."], ["goodwill", "average profit", "super profit", "capitalization", "normal profit", "years' purchase"]),
        ],
    },
    {
        "slug": "change-in-profit-sharing-ratio-methods-of-goodwill",
        "chapterNumber": 2,
        "chapter": "Change in Profit Sharing Ratio - Methods of Goodwill",
        "unit": "Unit 1: Accounting for Partnership Firms",
        "topics": [
            topic("sacrificing and gaining ratio", "Calculate sacrificing and gaining ratio when existing partners change ratio.", "Explain why gaining partners compensate sacrificing partners for goodwill.", "A, B and C change from old ratio to a new ratio and goodwill is valued.", ["Sacrificing ratio is old share minus new share.", "Gaining ratio is new share minus old share.", "Gaining partners compensate sacrificing partners for their loss of share in goodwill.", "Goodwill adjustment is made through capital or current accounts without raising goodwill account.", "The total debit to gaining partners equals total credit to sacrificing partners."], ["Sacrifice is new share minus old share.", "All partners always sacrifice equally.", "Goodwill is credited to gaining partners."], ["old ratio", "new ratio", "sacrificing ratio", "gaining ratio", "goodwill adjustment"]),
            topic("revaluation on change in ratio", "State the need for revaluation when profit sharing ratio changes.", "Prepare the treatment of revaluation profit or loss.", "Assets and liabilities are revalued before a new profit sharing ratio is adopted.", ["Revaluation records changes in values of assets and liabilities.", "Increase in asset or decrease in liability is credited to revaluation account.", "Decrease in asset or increase in liability is debited to revaluation account.", "Revaluation profit or loss is transferred to old partners in old ratio.", "The balance sheet is prepared after giving effect to revised values."], ["Revaluation profit is shared in new ratio.", "Only gaining partners get revaluation profit.", "Liability increase is credited to revaluation account."], ["revaluation account", "assets", "liabilities", "old ratio", "balance sheet"]),
            topic("reserves accumulated profits and losses", "Treat reserves and accumulated profits on change in ratio.", "Calculate partner-wise distribution of reserve and loss balances.", "A firm changes ratio with general reserve and Profit and Loss debit balance in books.", ["Accumulated profits and reserves belong to old partners in old ratio.", "Accumulated losses are debited to old partners in old ratio.", "General reserve is credited to partners' capital or current accounts.", "Profit and Loss debit balance is debited to partners' capital or current accounts.", "Treatment is completed before applying the new ratio."], ["Reserves are shared in new ratio.", "Accumulated losses are credited to partners.", "Only sacrificing partners receive reserve."], ["general reserve", "accumulated profit", "accumulated loss", "old ratio", "capital accounts"]),
            topic("balance sheet after change in ratio", "Identify items shown in the balance sheet after change in ratio.", "Build a board-style answer for preparing the revised balance sheet.", "A question asks for revaluation account, capital accounts and balance sheet after ratio change.", ["The revised balance sheet shows assets and liabilities at adjusted values.", "Partner capital/current accounts reflect goodwill, reserves and revaluation adjustments.", "Goodwill should be adjusted according to AS 26 treatment in the syllabus.", "New profit sharing ratio is used for future profits only.", "Balance sheet totals must agree after all adjustments."], ["Future profits are still shared in old ratio.", "Goodwill account is always raised permanently.", "Balance sheet ignores current account balances."], ["revised balance sheet", "adjusted values", "capital accounts", "AS 26", "new ratio"]),
        ],
    },
    {
        "slug": "admission-of-a-partner",
        "chapterNumber": 3,
        "chapter": "Admission of a Partner",
        "unit": "Unit 1: Accounting for Partnership Firms",
        "topics": [
            topic("new profit sharing ratio and sacrifice", "Calculate new ratio and sacrificing ratio on admission.", "Explain the effect of admission on existing partners' profit shares.", "A new partner is admitted for a fixed share of future profits.", ["Admission changes the old profit sharing ratio.", "The new partner receives an agreed share of future profits.", "Old partners sacrifice part of their share to the new partner.", "Sacrificing ratio is used for goodwill compensation.", "Future profits are distributed in the new ratio."], ["Admission never changes old ratio.", "Gaining ratio is used on admission.", "New partner compensates only one partner always."], ["admission", "new ratio", "sacrificing ratio", "goodwill", "future profits"]),
            topic("goodwill on admission", "Treat goodwill brought in by a new partner.", "Apply AS 26 treatment for goodwill on admission.", "A new partner brings premium for goodwill in cash.", ["Premium for goodwill is credited to sacrificing partners in sacrificing ratio.", "If goodwill is not brought fully, adjustment is made through capital or current accounts.", "Existing goodwill in books is written off among old partners in old ratio.", "Goodwill should not remain raised unless permitted by treatment.", "The answer must separate cash premium and capital contribution."], ["Goodwill premium is credited to new partner.", "Existing goodwill is written off in new ratio.", "Cash brought as capital is goodwill."], ["premium for goodwill", "sacrificing partners", "AS 26", "old ratio", "capital contribution"]),
            topic("revaluation and reserves on admission", "Treat revaluation and accumulated items on admission.", "Prepare the sequence of admission adjustments.", "Assets are revalued and reserves exist at the time of admission.", ["Revaluation profit or loss is transferred to old partners in old ratio.", "Reserves and accumulated profits are credited to old partners.", "Accumulated losses are debited to old partners.", "New partner does not share past profits or losses.", "Adjusted capital accounts are used to prepare the new balance sheet."], ["New partner receives old reserve.", "Revaluation profit is shared in new ratio.", "Accumulated loss is credited to old partners."], ["revaluation", "old partners", "reserves", "accumulated losses", "balance sheet"]),
        ],
    },
    {
        "slug": "retirement-and-death-of-a-partner",
        "chapterNumber": 4,
        "chapter": "Retirement and Death of a Partner",
        "unit": "Unit 1: Accounting for Partnership Firms",
        "topics": [
            topic("gaining ratio on retirement", "Calculate gaining ratio after retirement.", "Explain why continuing partners compensate the retiring partner for goodwill.", "A partner retires and the remaining partners acquire the retiring partner's share.", ["Gaining ratio shows the increase in continuing partners' profit shares.", "It is calculated as new share minus old share.", "Continuing partners compensate the retiring partner for goodwill in gaining ratio.", "The retiring partner's capital account is credited for his share of goodwill.", "Future profits are shared by continuing partners in the new ratio."], ["Retiring partner compensates continuing partners.", "Gaining ratio is old share minus new share.", "Goodwill is ignored on retirement."], ["retirement", "gaining ratio", "continuing partners", "goodwill", "new ratio"]),
            topic("retiring partner loan account", "Prepare the retiring partner's capital and loan account treatment.", "Sequence the settlement of amount due to a retiring partner.", "A retiring partner's final balance is partly paid and the balance is transferred to loan.", ["The retiring partner's capital account is adjusted for goodwill, reserves and revaluation.", "Amount due to retiring partner may be paid immediately or transferred to loan account.", "Loan account records unpaid balance due to the retiring partner.", "Payment reduces bank/cash balance.", "The balance sheet shows the loan as a liability until paid."], ["Retiring partner loan is an asset.", "Final capital balance is ignored.", "Payment increases cash balance."], ["capital account", "loan account", "amount due", "liability", "payment"]),
            topic("death of a partner", "Calculate deceased partner's share of profit till date of death.", "Prepare the deceased partner's capital and executor account treatment.", "A partner dies during the year and profit up to date of death must be credited.", ["Deceased partner's share of profit is calculated up to the date of death.", "The deceased partner's capital account is credited for profit share, goodwill and other dues.", "It is debited for drawings and amounts payable by the partner.", "Final amount due is transferred to executor's account.", "Executor's account is settled according to payment terms."], ["Executor account is an expense.", "Profit till death is never credited.", "Drawings increase amount due to deceased partner."], ["deceased partner", "profit till death", "executor account", "capital account", "settlement"]),
        ],
    },
    {
        "slug": "dissolution-of-partnership-firm",
        "chapterNumber": 5,
        "chapter": "Dissolution of Partnership Firm",
        "unit": "Unit 1: Accounting for Partnership Firms",
        "topics": [
            topic("realisation account", "Prepare the purpose and format logic of Realisation Account.", "Classify assets, liabilities and expenses in dissolution.", "A firm is dissolved and assets are realised while liabilities are paid.", ["Realisation Account records sale of assets and payment of liabilities.", "Assets except cash/bank are transferred to the debit side of Realisation Account.", "Liabilities to outsiders are transferred to the credit side.", "Realisation expenses are debited unless borne personally by a partner.", "Realisation profit or loss is transferred to partners' capital accounts in profit sharing ratio."], ["Cash is transferred to Realisation Account.", "Realisation profit is shared in capital ratio.", "Outside liabilities are ignored."], ["realisation account", "assets", "liabilities", "expenses", "profit sharing ratio"]),
            topic("partner capital and cash bank accounts", "Settle partner capital accounts and cash/bank account on dissolution.", "Arrange the settlement sequence after realisation.", "A dissolution question gives realised values, paid liabilities and partner capitals.", ["After realisation, partner capital accounts are adjusted for profit or loss on realisation.", "Partner loans are paid before partner capital balances.", "Deficiency of a partner is brought in by that partner unless otherwise stated.", "Cash/Bank Account records receipts from asset sale and payments to liabilities and partners.", "All accounts should close after dissolution settlement."], ["Capital is paid before external liabilities.", "Partner loan is ignored.", "Cash account need not balance."], ["capital settlement", "cash bank account", "partner loan", "deficiency", "closing accounts"]),
        ],
    },
    {
        "slug": "accounting-for-share-capital",
        "chapterNumber": 6,
        "chapter": "Accounting for Share Capital",
        "unit": "Unit 2: Accounting for Companies",
        "topics": [
            topic("issue and allotment of shares", "Record issue and allotment of equity and preference shares.", "Apply accounting treatment for oversubscription and undersubscription.", "A company issues shares at premium and receives applications above the offered shares.", ["Share capital is recorded according to application, allotment and call stages.", "Oversubscription requires allotment or refund according to question terms.", "Securities premium is credited separately when shares are issued at premium.", "Calls in arrears reduce paid-up capital disclosure.", "Calls in advance are shown separately as a liability."], ["Premium is debited to share capital.", "Calls in arrears increase paid-up capital.", "Oversubscription means shares are cancelled entirely."], ["application", "allotment", "securities premium", "calls in arrears", "calls in advance"]),
            topic("forfeiture and reissue", "Treat forfeiture and reissue of shares.", "Calculate capital reserve on reissue of forfeited shares.", "A shareholder fails to pay allotment/call money and forfeited shares are reissued.", ["Forfeiture cancels shares for non-payment of calls.", "Share capital is debited with called-up amount on forfeiture.", "Forfeited shares account is credited with amount received.", "Discount on reissue cannot exceed amount forfeited on those shares.", "Profit on reissue is transferred to capital reserve."], ["Forfeiture is made for overpayment.", "Capital reserve is a revenue profit.", "Discount on reissue has no limit."], ["forfeiture", "reissue", "called-up amount", "forfeited shares", "capital reserve"]),
            topic("balance sheet disclosure", "Disclose share capital in company balance sheet.", "Classify authorised, issued, subscribed, called-up and paid-up capital.", "A company has calls in arrears and securities premium at year end.", ["Share capital is disclosed as per Schedule III headings.", "Authorised capital is the maximum capital in the memorandum.", "Subscribed capital shows shares subscribed by shareholders.", "Called-up capital is the amount demanded by the company.", "Paid-up capital is called-up capital less calls in arrears."], ["Authorised capital equals cash received.", "Paid-up capital includes calls in arrears.", "Securities premium is shown as share capital."], ["Schedule III", "authorised capital", "subscribed capital", "called-up capital", "paid-up capital"]),
        ],
    },
    {
        "slug": "accounting-for-debentures",
        "chapterNumber": 7,
        "chapter": "Accounting for Debentures",
        "unit": "Unit 2: Accounting for Companies",
        "topics": [
            topic("issue of debentures", "Record debentures issued at par, premium and discount.", "Prepare journal logic for issue of debentures for cash and consideration other than cash.", "A company issues debentures to vendors and to public subscribers.", ["Debentures are long-term borrowings of a company.", "Issue at par records debenture liability at face value.", "Premium on issue is credited separately.", "Discount or loss on issue is written off as prescribed in the syllabus note.", "Debentures issued for consideration other than cash settle vendor liability."], ["Debentures are ownership capital.", "Premium on issue is an expense.", "Vendor issue always creates cash inflow."], ["debentures", "par", "premium", "discount", "vendor"]),
            topic("collateral security and interest", "Explain debentures issued as collateral security.", "Calculate and record interest on debentures.", "A company gives debentures as secondary security for a bank loan.", ["Collateral security is additional or secondary security for a loan.", "Debentures issued as collateral may be disclosed by note or by accounting entry.", "Interest on debentures is a charge against profit.", "TDS concept is excluded from the syllabus.", "Outstanding interest is shown as a liability."], ["Collateral debentures are primary capital.", "Interest is appropriation of profit.", "TDS must be calculated in this syllabus."], ["collateral security", "bank loan", "interest on debentures", "charge", "liability"]),
        ],
    },
    {
        "slug": "financial-statements-of-a-company",
        "chapterNumber": 8,
        "chapter": "Financial Statements of a Company",
        "unit": "Unit 3: Analysis of Financial Statements",
        "topics": [
            topic("company balance sheet and statement of profit and loss", "Identify major headings of company financial statements.", "Classify items under Schedule III headings.", "A question gives a list of company assets, liabilities, income and expenses.", ["Company financial statements include Balance Sheet and Statement of Profit and Loss.", "Balance Sheet is prepared with major headings and sub-headings as per Schedule III.", "Statement of Profit and Loss reports revenue, expenses and profit.", "Exceptional and extraordinary items are excluded from this syllabus scope.", "Correct classification improves financial statement analysis."], ["Schedule III is not used for companies.", "Extraordinary items are included in this syllabus.", "All assets are shown under current assets."], ["Balance Sheet", "Statement of Profit and Loss", "Schedule III", "classification", "company financial statements"]),
        ],
    },
    {
        "slug": "financial-statement-analysis",
        "chapterNumber": 9,
        "chapter": "Financial Statement Analysis",
        "unit": "Unit 3: Analysis of Financial Statements",
        "topics": [
            topic("meaning tools and limitations", "State meaning, objectives and limitations of financial statement analysis.", "Compare comparative statements, common-size statements, ratio analysis and cash-flow analysis.", "Management wants to analyse trends, structure and liquidity from company statements.", ["Financial statement analysis studies relationships and trends in financial data.", "Comparative statements show changes over time.", "Common-size statements show each item as a percentage of a base.", "Ratio analysis studies relationships between selected items.", "Analysis has limitations because it depends on accounting data and policies."], ["Analysis removes all accounting limitations.", "Common-size statement compares only two years.", "Ratio analysis is same as cash flow statement."], ["financial analysis", "comparative statement", "common-size statement", "ratio analysis", "limitations"]),
        ],
    },
    {
        "slug": "accounting-ratios",
        "chapterNumber": 10,
        "chapter": "Accounting Ratios",
        "unit": "Unit 3: Analysis of Financial Statements",
        "topics": [
            topic("liquidity and solvency ratios", "Calculate current ratio, quick ratio and solvency ratios.", "Interpret liquidity and solvency from given financial data.", "A company provides current assets, inventories, current liabilities, debt and equity.", ["Current ratio measures current assets against current liabilities.", "Quick ratio excludes inventory and prepaid expenses where applicable.", "Debt-equity ratio measures debt relative to shareholders' funds.", "Interest coverage ratio measures ability to meet finance cost from earnings.", "Ratios must be interpreted with business context."], ["Quick ratio includes closing inventory.", "Debt-equity ratio is current assets divided by current liabilities.", "Higher interest coverage always means loss."], ["current ratio", "quick ratio", "debt-equity ratio", "interest coverage", "solvency"]),
            topic("activity and profitability ratios", "Calculate turnover and profitability ratios.", "Interpret operating efficiency and profitability from ratios.", "A company gives sales, cost of goods sold, inventory, receivables, payables and profit figures.", ["Inventory turnover ratio links cost of goods sold with average inventory.", "Trade receivables turnover ratio measures speed of collection.", "Working capital turnover ratio relates revenue to working capital.", "Gross profit ratio and net profit ratio measure profitability on revenue.", "Return on investment measures profit relative to capital employed."], ["Inventory turnover uses only closing inventory.", "Gross profit ratio uses net profit after tax.", "ROI ignores capital employed."], ["turnover ratio", "gross profit ratio", "net profit ratio", "ROI", "working capital"]),
        ],
    },
    {
        "slug": "cash-flow-statement",
        "chapterNumber": 11,
        "chapter": "Cash Flow Statement",
        "unit": "Unit 5: Cash Flow Statement",
        "topics": [
            topic("cash flow statement indirect method", "Prepare cash flow statement using indirect method.", "Classify operating, investing and financing activities.", "A company gives comparative balance sheets and statement of profit and loss adjustments.", ["Cash Flow Statement reports cash inflows and outflows during a period.", "Activities are classified as operating, investing and financing.", "Indirect method starts with profit and adjusts non-cash and non-operating items.", "Depreciation is added back while calculating cash from operating activities.", "Cash and cash equivalents include items defined by AS 3."], ["Depreciation is a cash outflow.", "Indirect method starts with sales revenue.", "All bank overdrafts are cash equivalents in every case."], ["AS 3", "operating activities", "investing activities", "financing activities", "indirect method"]),
        ],
    },
    {
        "slug": "computerised-accounting-system",
        "chapterNumber": 12,
        "chapter": "Computerised Accounting System",
        "unit": "Unit 4: Computerised Accounting",
        "topics": [
            topic("overview and software packages", "State features and structure of a computerised accounting system.", "Compare generic, specific and tailored accounting software.", "A firm wants software for vouchers, ledgers, reports and controls.", ["Computerised Accounting System applies accounting through software and databases.", "CAS improves speed, accuracy, storage and report generation.", "Generic software serves common needs.", "Specific software serves a particular industry or business requirement.", "Tailored software is customised for special user needs."], ["CAS removes the need for controls.", "Generic software is made for one firm only.", "Tailored software cannot be changed."], ["CAS", "software package", "generic", "specific", "tailored"]),
            topic("spreadsheet and accounting applications", "Use electronic spreadsheet features in accounting applications.", "Identify spreadsheet use in BRS, asset accounting, loan schedule and ratio analysis.", "A student uses spreadsheet formulas and charts for accounting information.", ["Electronic spreadsheets organise data in rows and columns.", "Formulae and functions help accounting calculations.", "Spreadsheets can support bank reconciliation and asset accounting.", "Loan repayment schedules and ratio analysis can be prepared using spreadsheets.", "Graphs, charts and diagrams represent accounting data visually."], ["Spreadsheets cannot use formulae.", "Charts are excluded from accounting data representation.", "Spreadsheet is only for typing text."], ["spreadsheet", "formula", "bank reconciliation", "ratio analysis", "charts"]),
            topic("using computerized accounting system", "List steps in installing and using CAS.", "Explain codification, hierarchy, data validation and security features.", "A business creates ledger accounts and enters vouchers in CAS.", ["CAS use involves installation, codification and creation of account heads.", "Hierarchy of account heads organises ledgers logically.", "Data entry must be validated and verified.", "Closing and opening entries help prepare final accounts.", "Security features protect accounting data from misuse."], ["Security is optional in accounting systems.", "Validation means deleting data.", "Hierarchy of accounts is unrelated to reports."], ["installation", "codification", "hierarchy", "validation", "security"]),
        ],
    },
]


def output_path(chapter: dict[str, Any]) -> str:
    return f"data/practice/class-12/accountancy-syllabus-question-bank/{chapter['chapterNumber']:02d}-{chapter['slug']}.json"


def make_payload(chapter: dict[str, Any], relative: str) -> dict[str, Any]:
    meta = {
        "root": r"C:\Users\acer\Downloads",
        "pdfPath": PDF_PATH,
        "classLevel": 12,
        "stream": "Commerce",
        "subject": "Accountancy",
        "book": BOOK,
        "chapter": chapter["chapter"],
        "chapterNumber": chapter["chapterNumber"],
    }
    payload = dataset(meta, chapter["topics"], ROOT / relative)
    payload["source"]["syllabusUnit"] = chapter["unit"]
    payload["source"]["syllabusReference"] = SYLLABUS_URL
    payload["coverage"]["generationMode"] = "class-12-accountancy-syllabus-question-bank"
    payload["coverage"]["syllabusUnit"] = chapter["unit"]
    return payload


def upsert_catalog(path: str, payload: dict[str, Any]) -> None:
    catalog_path = ROOT / "data/catalog/content-catalog.json"
    if not catalog_path.exists():
        return
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    source = payload["source"]
    entry = {
        "id": path.removesuffix(".json"),
        "jsonPath": path,
        "hasJson": True,
        "activityCount": len(payload["activities"]),
        "classLevel": source["classLevel"],
        "stream": source["stream"],
        "subject": source["subject"],
        "book": source["book"],
        "chapter": source["chapter"],
        "chapterNumber": source["chapterNumber"],
        "pdfPath": source["pdfPath"],
        "relativePath": "Accountancy_SrSec_2025-26.pdf",
        "status": "active",
    }
    datasets = catalog.setdefault("datasets", [])
    for index, existing in enumerate(datasets):
        if existing.get("jsonPath") == path:
            datasets[index] = {**existing, **entry}
            break
    else:
        datasets.append(entry)
    catalog["generatedAt"] = int(time.time())
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def upsert_active(path: str) -> None:
    active_path = ROOT / "data/catalog/active-datasets.json"
    payload = {"activeDatasets": []}
    if active_path.exists():
        payload = json.loads(active_path.read_text(encoding="utf-8"))
    entry = {
        "id": path.removesuffix(".json"),
        "jsonPath": path,
        "status": "active",
        "approvedBy": "accountancy-syllabus-question-bank",
        "notes": "Class 12 Accountancy syllabus-based question bank generated from Accountancy_SrSec_2025-26.pdf.",
    }
    active = payload.setdefault("activeDatasets", [])
    for index, existing in enumerate(active):
        if existing.get("jsonPath") == path:
            active[index] = entry
            break
    else:
        active.append(entry)
    active_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    for chapter in CHAPTERS:
        relative = output_path(chapter)
        payload = make_payload(chapter, relative)
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        upsert_catalog(relative, payload)
        upsert_active(relative)
        print(f"Wrote {relative} ({len(payload['activities'])} activities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
