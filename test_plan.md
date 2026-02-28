# Test Plan

CS-487-01 2/28/2026

Team E:

- Peter Capuzzi
- Andrew Chang-Dewitt
- Derrick Taylor
- Rinat Verezub

## 1. Summary

### 1.1 Testing Strategy

Our testing strategy will ensure accuracy and usability of the system.
It will be tested at 3 primary layers:

- Unit Testing: Verification of individual logic components such as
  budget calculations, interest estimators, and financial health score
  formulas.
- Integration Testing: Insurance of correct data flow between modules,
  such as "Shared Budgets" and individual user accounts.
- System Testing: Validation of complete user workflows from initial
  account setup to receiving financial health insights.

Testing will include both Functional Testing to ensure every button and
calculation works as expected, as well as Non-Functional Testing,
focusing on UI responsiveness and performance. For this prototype, we
will place emphasis on logical accuracy and user flow rather than
real-time backend synchronization.

### 1.2 Boundaries and Edge Cases

Our financial application will handle edge cases correctly to maintain
user trust and application reputation. We will test the system under the
following boundary conditions:

- Zero Values: Setting a category budget to \$0.00 and verifying system
  behavior.
- Extreme Transactions: Entering extremely large deposits (e.g.
  \$10,000,000) to test numeric limits and UI formatting.
- Empty Accounts: Accessing dashboards before any transactions are
  entered to ensure helpful guidance is displayed.
- Account Deletion: Removing an account that is linked to a "Shared
  Budget" and verifying proper reassignment or error handling.

These tests will ensure stability, prevent crashes, and confirm
mathematical reliability under extreme conditions.

### 1.3 Normal and Exceptional Cases

In normal case testing, the system verifies expected user behavior. Here
is an example:

- A user logs a \$40 grocery expense.
- The "Food" budget decreases accordingly, and the system updates
  totals.
- An alert triggers when 80% of the category budget is reached.
- Data persists after logging out and re-logging in.

In exceptional case testing, the system ensures graceful error handling.
Examples include:

- Entering a negative value in a deposit field.
- Attempting to submit a transaction with missing requirement fields.
- Two users attempt to edit the same "Shared Budget" transaction
  simultaneously.

The system must prevent invalid entries and display clear error
messages. For shared conflicts, the system should prevent data
overwriting and notify users accordingly.

### 1.4 Test Data and Environment

This prototype will not integrate with real banks, so we will use
synthesized test data. This includes:

- Mock transaction CSV files
- Predefined user personas with varying income and spending patterns
- Simulated shared budgets and investment entries

Test Environment:

- Development: Local machines for unit and integration testing.
- Staging: Hosted web prototype (e.g. a hosted Vercel instance) that
  simulates real user interaction and performance.

Security Considerations: No real personal or financial data should be
used. All test data will be fictional. We will also test user isolation
to ensure one user cannot access another user's financial information
(unless explicitly added to a "Shared Budget").

## 2. Test Cases

### 2.1 New User sign-up & onboarding

#### User must be able to sign up to create a new user login & profile

**Initial state:** No user account exists. App is displaying the sign-up interface to a new visitor.

**Execution steps:**

1. User enters valid information (email, password, etc.) in the sign-up form.
2. User submits the form.

**Expected final state:**

- A new user account and profile is created.
- User is logged in and redirected to onboarding steps.

#### User should be guided in adding their first bank account

**Initial state:** New user has just completed sign-up and has no bank accounts linked.

**Execution steps:**

1. App prompts user to add a bank account as the first onboarding step.
2. User follows instructions to link a bank account (either by connecting directly or entering info manually).

**Expected final state:**

- User has added at least one bank account.
- App confirms successful connection and allows proceeding to next onboarding step.

#### User should be guided in creating their first budget categories

**Initial state:** User has signed up and added a bank account but has no budget categories defined.

**Execution steps:**

1. App prompts user to define budget categories during onboarding.
2. User enters information for at least one budget category (e.g., "Groceries").

**Expected final state:**

- At least one budget category exists for the user.
- App confirms category creation and onboarding proceeds or concludes.

### 2.2 Associating spending accounts/credit lines/investment assets

#### Add new bank accounts, lines of credit, or investment accounts/assets

**Initial state:** User account exists. The app presents an option to add a new financial account. User has at 0+ other account already linked.

**Execution steps:**

1. User navigates to the 'Add Account' screen.
2. User selects the type of new account (bank, credit, investment).
3. User enters required account details and submits.

**Expected final state:**

- The new account is listed under the correct category (bank, credit, investment, or cash) linked to the user profile.

#### Remove or mark bank accounts/credit lines/investment accounts as closed

**Initial state:** User has 1+ accounts (bank, credit, investment, or cash) linked to the profile.

**Execution steps:**

1. User selects an account to remove or mark closed.
2. User uses the UI to perform the remove/close action.

**Expected final state:**

- The selected account is either removed or clearly marked as closed in the user's account listings and is excluded from future transaction imports.

#### Create a cash spending account for manually tracking cash spending

**Initial state:** User profile exists with at least one digital account.

**Execution steps:**

1. User navigates to account management and selects the option to add a new account.
2. User selects "Cash" as the account type.
3. User provides a name/description for the account.

**Expected final state:**

- A cash account is added to the account list.
- Future manual transactions can be assigned to this cash account.

### 2.3 Tracking account transactions

#### Batch import transactions

**Initial state:** User has at least one financial account and some external file (e.g. CSV, JSON, etc.) of transaction records.

**Execution steps:**

1. User navigates to the transactions or import interface.
2. User uploads transaction file and starts the import.
3. App processes the file and presents a summary for review before saving imported transaction data.

**Expected final state:**

- All valid transactions from the file are associated with the appropriate account & presented in a summary.
- Final summary includes errors, showing transactions that couldn't be reported, and warnings, showing fields that were ignored for specific transactions.
- Final summary allows user to approve all changes, select only some subset of the changes for approval, and/or make manual edits to the imported data before approving (including picking a budget category from which to allocate the funds for any debit transaction).
- When user approves any of the summarized changes, the transactions are added to their associated accounts & are visible in the appropriate transactions list views.

#### Edit (split, rename, add notes, etc.) transaction records

**Initial state:** User account and at least one transaction already imported/displayed.

**Execution steps:**

1. User opens a transaction entry in the transaction history.
2. User edits details (renames, splits by category, adds a note).

**Expected final state:**

- Transaction record is updated in the system and new details reflected in reports/budget category assignments.

#### Manually add a new transaction record

**Initial state:** User has at least one account set up. No transaction is yet added for today.

**Execution steps:**

1. User navigates to transactions and selects "Add Transaction".
2. User completes required transaction details and submits.

**Expected final state:**

- The new transaction is reflected in the transaction history for the selected account.

#### Delete a transaction record

**Initial state:** At least one transaction exists for a user account.

**Execution steps:**

1. User locates a transaction from the transaction list.
2. User chooses to delete it via the UI.

**Expected final state:**

- The selected transaction is removed from the account's transaction list and all reports/balances updated.

#### Automatically import transactions from associated participating bank accounts/credit cards

**Initial state:** User has an associated supported bank or credit card account.

**Execution steps:**

1. Scheduled automatic import is triggered or user initiates a manual sync.
2. App fetches transactions from external provider for the linked account(s).
3. New transactions (not previously seen) are added to the system.

**Expected final state:**

- All new transactions from the bank/credit account appear in the transaction history for that account.
- No duplicate or missing transactions.

#### See when transactions are transfers between associated accounts or payments to associated credit lines

**Initial state:** User has two or more accounts linked and one or more pairwise transfer/payment transactions have occurred.

**Execution steps:**

1. User imports or manually adds a transfer/payment transaction between two associated accounts (e.g., transfer from checking to credit card).
2. App processes and flags these transactions appropriately as transfers or payments between associated accounts.

**Expected final state:**

- Transactions between accounts are flagged and not shown as "spending" or "income" in overviews for the user.
- Transaction histories for both source and destination accounts reflect the transfer relationship.

### 2.4 Budgeting plans & savings goals

#### Make ad-hoc adjustments to budget categories

**Initial state:** User has a complete budgeting plan with 1+ categories and a total balance across all associated accounts that is greater than 0.

**Execution steps:**

1. User selects a budget category to adjust.
2. User selects an amount to allocate into or take out of the category.
3. User selects another category (or the "Unallocated"—a.k.a. default or "Safe-to-Spend") to take the newly allocated amount from or to allocate for the amount being removed from this category.

**Expected final state:**

- The new value is saved for this category & the other category.
- Associated forecasts for effected categories & total "Safe-to-Spend" balances include the newly updated amounts.

#### Add estimated income projections/schedules to budgeting plans

**Initial state:** User has a budget plan without any projected future income entries.

**Execution steps:**

1. User navigates to budgeting plan settings.
2. User enters an estimated income value, optionally with a future recurring schedule, and saves.

**Expected final state:**

- Budget categories & savings goals include estimated income when making projections about when the category/goal will be satisfied.
- Plan now displays estimated income(s) and optionally anticipated recurring inflows on summaries/projections.

#### Associate schedules with budget categories

**Initial state:** Budgeting plan exists and already has at least one category, or User is creating a new category.

**Execution steps:**

1. User chooses a category and sets a schedule (e.g. monthly, every 2 weeks).
2. User saves the changes.

**Expected final state:**

- The category displays the next scheduled due date and amount.
- Summaries adjust to show category requirements by next due date.

#### See how much money is available to spend in each budget category

**Initial state:** User has at least one budget category or savings goal with allocations and some transaction history for the current period.

**Execution steps:**

1. User navigates to the budget overview screen.

**Expected final state:**

- The available amount for each category is correctly calculated and displayed (allocation for current period minus spending).

#### See if on track for each budget by next scheduled date

**Initial state:** At least one category has a required amount and a defined schedule, and 0+ transactions are associated with the category for the category's current spending period.

**Execution steps:**

1. User navigates to budget overview or category detail for a scheduled category.
2. App calculates the projected remaining amount needed to meet the goal by the scheduled date based on current spend and schedule.

**Expected final state:**

- App visually indicates to the user (e.g., progress bar, status icon) if they are on track or behind for the next scheduled category goal.
- If the category is _not_ on track, the User is prompted to make changes (e.g. allocate additional funds from another category/goal, update target amount, etc.)

#### Allocated amounts for each category & savings goal updated automatically on new income

**Initial state:** User has defined multiple budget categories and/or savings goals with allocations. There is at least one bank account associated. No new income transactions present for the current period.

**Execution steps:**

1. User receives a new income transaction in an associated bank account.
2. App detects the new income transaction and triggers allocation update logic.

**Expected final state:**

- Allocated amounts for each category and/or savings goal are recalculated using the preconfigured allocation logic (e.g., percentage, waterfall, user rules).
- Updated allocations are reflected in the category/savings goal balances and budget overview after the income transaction is recorded.

#### Exclude balances & income in designated accounts from automatic allocation for recurring expenses

**Initial state:** User has 1+ accounts designated as 'excluded' from automatic allocation & 1+ recurring expense budget category.

**Execution steps:**

1. User designates account(s) as excluded from automatic allocation in account settings.
2. New income is posted to a non-excluded account or recalculation of allocations is triggered (e.g., by adding a new recurring expense, editing target amounts for recurring an existing expense, or manual refresh).
3. App performs allocation update without considering the excluded account(s) transactions.

**Expected final state:**

- Balances and income in the excluded accounts are not counted or used for automatic allocation when calculating available amounts for categories marked as recurring expenses.
- UI and reports reflect only included accounts for such allocations.

#### Differentiate between recurring expenses/budget categories & longer-term savings goals

**Initial state:** User has created their profile & may have 0+ associated bank accounts/credit lines and 0+ budget categories created already.

**Execution steps:**

1. User tries to add or edit a budget category and is given an option to designate it as a recurring expense or one-time savings goal.
2. User selects both types in different cases.

**Expected final state:**

- Selected categories are clearly marked as either recurring expenses or savings goals in the UI and in associated summaries.

### 2.5 Shared budgeting plans

#### User can join or invite another user to a shared budget

**Initial state:** User account exists. A valid invitation mechanism is in place. Another user's account is available.

**Execution steps:**

1. User initiates an invitation for another user or accepts an invitation to join a shared budget.
2. Invited user receives notification/invite and accepts.

**Expected final state:**

- Both users now see the shared budget on their dashboards, with permissions for both as members.
- Both users still see their individual budgets as well (but not one-another's individual budgets).
- Both users can now choose categories from the shared budget when associating a transaction with a budget category.

#### Keep personal accounts & budgets separate from shared budgets

**Initial state:** User is a member of both a shared budget and has a personal budget/account list.

**Execution steps:**

1. User navigates between dashboards for personal and shared budgets.
2. User attempts to add or view accounts to each space.

**Expected final state:**

- Shared and personal budgets/accounts are clearly separated in the UI and cannot be shared or mixed by mistake.

#### User can leave a shared budget

**Initial state:** User is a member of at least one shared budget with other active participants.

**Execution steps:**

1. User selects the shared budget in the UI.
2. User chooses to leave and confirms the action.

**Expected final state:**

- User is no longer listed as a member of the shared budget.
- Budget persists for other members.

### 2.6 Analysis, advice, & financial planning

#### See reports of trends, changes in spending patterns, & other useful statistics

**Initial state:** User has substantial transaction history (multiple categories, months, and accounts).

**Execution steps:**

1. User navigates to the analytics/reporting section of the application.
2. App generates and displays various summary statistics, visualizations (e.g., graphs), and trends based on user data.

**Expected final state:**

- User sees visualizations and tables highlighting spending patterns, category changes, and historical trends.

#### Given recommendations for changes to improve outcomes

**Initial state:** User has data indicating missed goals (e.g., overspent, missed savings targets).

**Execution steps:**

1. User visits advice/planning/recommendations area after running regular budget cycle.
2. App analyzes trends, spending, and goals then generates personalized written recommendations (e.g., "reduce spending in X", "increase savings to Y") and suggests concrete actions.

**Expected final state:**

- User is presented with a clear list of suggestions with rationale linked to their activity and goals.

## 3. Personas

### 3.1 Young Adult

**Name:** Alex Nguyen

**Age:** 21

**Occupation:** Senior Undergraduate Student and Part-time Barista

**Income:** \$1,200 - \$1,500 / month (variable)

**Financial Situation:**

Alex manages part-time income, a small parental stipend, and shared
apartment expenses. Minimal savings and a limited credit history cause
financial stress and feeling of instability.

**Goals and Behavior:**

- Track spending and avoid overdraft fees
- Monitor small student loan payments at a large scale
- Manage shared household expenses efficiently
- Display quick and actionable insights instead of detailed financial
  analysis

**System Usage:**

- Checks financial health score to assess financial status quickly
- Uses shared budget for rent and utility tracking
- Configures alerts for overspending categories

**UX Assessment Approach:**

- Measures task completion for key actions (adding transactions,
  checking financial health scores, managing shared budgets, etc.)
- Observe navigation ease and use of alerts
- Collect feedback on dashboard clarity and confidence in financial
  management

### 3.2 Working Professional

**Name**: John Brown

**Age**: 38

**Occupation**: Senior Mechanical Engineer at Fictional Aerospace
Manufacturing Firm

**Income**: \$112,000 per year salary + \$8000 annual bonus

**Financial Situation**: John has a moderately complex financial
portfolio. Including a condo with a mortgage, a car loan, contributions
to a 401(k) plan, and a Roth IRA. He holds a brokerage account with both
ETF's and individual stocks. He maintains both a checking and high-yield
savings account with multiple different banks. He also has a small side
income stream from freelance CAD consulting. He tracks monthly expenses
consistently but finds it difficult to maintain a comprehensive overview
of his net worth and long-term projections because his financial data is
scattered across multiple platforms.

**Goals and Behavior**:

- Centralized Dashboard showing real-time net worth including
  investments, debts, and cash.
- Values automation, would prefer to minimize manual input.
- Checks finances 2-3 times per week, more frequently near bill due
  dates.
- Dislikes cluttered interfaces and expects reliability.
- Prioritizes long-term financial planning.

**System Usages**:

- Primarily accesses the application on his phone for quick checks, or
  his laptop for weekly financial reviews.
- Uses the application to monitor account balances, receive payment
  reminders, and track investments or net worth trends.
- Occasionally customizes dashboards and sets alerts for unusual
  transactions or reminders to limit spending.

**UX Assessment Approach**:

- Scenario-Based usability tests: Check functionality of tasks like
  linking multiple accounts, scheduling reminders, and analyzing
  spending categories.
- Cognitive Load assessments: Observe whether the UI could come across
  as cluttered or unprofessional, are data displays properly formatted
  for analytical purposes?
- Longitudinal testing: Monitor usage behavior over multiple sessions to
  evaluate if the application supports habit formation and long-term
  usage.
- Error Tolerance evaluations: Introduce sync delays or missing data
  scenarios to test system communication and overall reliability.

### 3.3 Retiree

**Name**: Martha Gumbholdt

**Age**: 67

**Occupation**: Retired Public-School Administrator at Fictional
Regional High School

**Income**: \~$52,000 per year. Combined from Pension, Social Security,
and Investment Withdrawals

**Financial Situation**: Martha owns a fully paid off home and one car.
She maintains one checking account, a savings account, a pension
distribution account, and an IRA that she makes periodic withdrawals
from. She has no current debts, and her primary concern is to ensure her
retirement savings last through her lifetime while covering fixed
expenses. She currently keeps a paper ledger of her financials but finds
it occasionally difficult to manage efficiently.

**Goals and Behavior**:

- Wants a simple and easy to understand way to view monthly income
  against expenses.
- Prefers stability and knowledge that her finances are reliable
  long-term but also has a minor gambling habit that contributes around
  \$200 a month to her expenses.
- Prefers simplicity, large text, clear graphics, and straightforward
  language.
- Overall inexperienced with technology, prefers applications with
  step-by-step guidance.
- Checks finances roughly once a week but occasionally forgets to do so.
- Motivated by security and stability over financial optimization.

**System Usages**:

- Primarily uses the application on a tablet at home for its larger
  screen size.
- Weekly reviews balances, budget status, and the completion status of
  recent withdrawals or transactions.
- Tracks pension payments, savings withdrawals, and gambling expenses to
  verify that she has stayed on budget.
- Rarely changes displays or customizes settings and prefers solid
  default configurations.

**UX Assessment Approach**:

- Guided-Usability testing: Observe her completion of various common
  tasks like checking account balances, viewing monthly spending, and
  confirming income deposits.
- Learnability Metrics: Evaluate her first-time understanding of the
  user interface without prior instruction to ensure the UI is easy to
  use for someone with low technological capabilities.
- Error Recovery testing: Assess how clear the system is when explaining
  mistakes and how she can easily correct them.
- Cognitive Load testing: Evaluate her mental state while using the
  application to ensure it is not confusing or frustrating to use by
  monitoring hesitation or repeated navigation attempts during usage.
- Support Interaction simulation: Test helpful features like tooltips,
  tutorials, or access to a customer support chatbot or human assistance
  for intuitive and reassuring assistance.

## 4. AI Transcripts

### 4.1 Peter Capuzzi

[Peter Capuzzi AI usage
transcription](https://chatgpt.com/share/699f83af-60e8-800a-bb00-d6283cc96430)

### 4.2 Andrew Chang-Dewitt

### 4.3 Derrick Taylor

### 4.4 Rinat Verezub

<https://gemini.google.com/share/cb85eb0123b6>
