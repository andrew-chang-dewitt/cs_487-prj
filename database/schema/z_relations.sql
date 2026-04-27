ALTER TABLE "category"
    ADD CONSTRAINT fk_user
        FOREIGN KEY(user_id)
            REFERENCES app_user(id)
            ON DELETE CASCADE;

ALTER TABLE "account"
    ADD CONSTRAINT fk_user
        FOREIGN KEY(user_id)
            REFERENCES app_user(id)
            ON DELETE CASCADE;

ALTER TABLE "transaction"
    ADD CONSTRAINT fk_account
        FOREIGN KEY(account_id)
            REFERENCES account(id)
            ON DELETE CASCADE;

ALTER TABLE "transaction"
    ADD CONSTRAINT fk_spent_from
        FOREIGN KEY(spent_from)
            REFERENCES category(id)
            ON DELETE SET NULL;
