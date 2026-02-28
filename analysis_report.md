# Analysis Report

CS-487-01 2/14/2026

Team E:

- Peter Capuzzi
- Andrew Chang-Dewitt
- Derrick Taylor
- Rinat Verezub

## 1. Summary

The purpose of this system is to engineer an intelligent personal
financial management application to assist users in tracking finances,
managing budgets and investments, monitoring overall financial health,
and receiving automated insights and alerts. The system is designed as a
prototype for purposes of demonstration.

The proposed system is a personal finance application that enables users
to:

- Track spending, deposits, cash flow, and financial trends
- Manage bills and investments
- Monitor real time financial health
- Receive automated alerts and insights based on financial behavior

The application is intended for users of all ages, from teenagers or
elderly users. While providing support for a broad audience, its primary
focus is on individuals managing their own personal finances.

## 2. User Categories

### 2.1 Young Adults

This category includes users aged approximately 18-25 years old, who are
just starting to manage their finances independently, often as beginners
to personal finance.

This user category is typically characterized by:

- Earning limited or part-time income
- Spending on student loans & tuition expenses
- Having less experience with finance apps
- Being generally comfortable with technology
- Preferring quick access to summaries and alerts

The primary features needs for this user group include:

- Spending breakdown by category of expense
- Budget tracking tools
- Low balance and overspending alerts
- Monthly trend summaries

### 2.2 Working Professionals

This user category includes people aged approximately 25-55 years old,
who are already acquainted with general financial knowledge and
management. Likely looking for a tool to help them manage increasingly
complex financial situations.

This user category is typically characterized by:

- Gainful employment and earning full time wages.
- Relatively complex financial situations with various elements.
- Physical assets, debts, differing account types, potentially multiple
  income sources.
- Experienced with financial technology.
- Preference for overall organizational capability.

The primary feature requirements for this group includes:

- Multiple asset, debt, and account tracking.
- Longer term schedules for debt repayments and financial balancing.
- An overall net worth tracker / display to neatly show different
  assets.
- Scheduled reminders for events like payday, due payments, etc.

### 2.3 Retirees

This user category includes people aged approximately 55+ years, who
have retired from full time employment and are looking to organize their
current finances.

This user category is typically characterized by:

- Physical assets, (Home, Cars, Savings, etc.)
- Likely a lack of debts.
- Lower experience with technology compared to younger user categories.
- Preference for usability over alerts or complexity.

The primary feature requirements for this group includes:

- Financial balance and budgeting break down to ensure lack of primary
  income source does not become a problem.
- Multiple account trackers for different account types (Savings,
  Pension, IRA, etc.)
- Accessible tools that allow for an easy-to-use service for someone
  with limited experience with financial technology.
- Asset trackers for potential alternative income, (Investments,
  part-time business, etc.)

## 3. Requirements

### 3.1 Functional Requirements

1.  New User sign-up & onboarding:
    - A new User must be able to sign up to create a new user login &
      profile
    - A new User should be guided in adding their first bank account
    - A new User should be guided in creating their first budget
      categories

2.  Associating spending accounts/credit lines/investment assets:
    - A User should be able to add new bank accounts, lines of credit, &
      investment accounts/assets
    - A User should be able to remove bank accounts/credit
      lines/investment accounts and/or mark them as closed
    - A User should be able to create a cash spending account for
      manually tracking cash spending

3.  Tracking account transactions:
    - A User should be able to batch import transaction records for
      tracking
    - A User should be able to edit (split, rename, add notes, etc.)
      transaction records
    - A User should be able to manually add a new transaction record
    - A User should be able to delete a transaction record
    - A User should be able to automatically import transactions from
      associated participating bank accounts/credit cards
    - A User should be able to see when transactions are transfers
      between associated accounts or payments to associated lines of
      credit

4.  Budgeting plans & savings goals:
    - A User should be able to differentiate between reoccurring
      expenses/budget categories & longer-term savings goals
    - A User should be able to make ad-hoc adjustments to budget
      categories to stay on track without drastic changes to their
      entire budgeting plan
    - A User should be able to add estimated income
      projections/schedules to their budgeting plans
    - A User should be able to associate schedules (weekly, every n
      weeks, monthly, every n days, etc.) with budget categories to
      indicate when & how often the target amount for the category is
      needed
    - A User should be able to see at a glance how much money they have
      remaining available to spend in each budget category
    - A User should be able to see at a glance if they are on track to
      meet the required amount for a budget category by its next
      scheduled date
    - A User should have allocated amounts for each category & savings
      goal updated automatically whenever a transaction including new
      income is added to an associated bank account
    - A User should be able to exclude balances & income in designated
      accounts from being used when automatically allocating for
      reocurring expenses

5.  Shared budgeting plans:
    - A User should be able to join or invite another User to a shared
      budget
    - A User should be able to keep their personal accounts & budget
      separate from any shared budgets they may be a part of
    - A User should be able to leave a shared budget

6.  Analysis, advice, & financial planning
    - A User should be able to see reports of trends, changes in
      spending patterns, & other useful statistics
    - A User should be given recommendations of changes (in their
      budgeting plan, spending habits, investments, etc.) they could
      make to better meet their goals

### 3.2 Non-functional Requirements

1.  Performance
    - Loads the dashboard within seconds under internet conditions
    - Process and display all transactions in real time

2.  Security
    - Encrypt all sensitive user data in transit and in storage
    - Secure authentication (password, 2FA etc.)
    - Log users out after inactivity

3.  Accessibility
    - Support screen readers with scalable text
    - Light or Dark mode
    - Fits website standards

4.  Compatibility
    - Accessible via modern web browsers and mobile devices
    - Support any browser type

5.  Reliability
    - Maintains its uptime during usage
    - Prevent data loss

6.  Usability
    - Simple and intuitive user interface
    - Simple tasks require little steps
    - Could include tooltips or guidance
