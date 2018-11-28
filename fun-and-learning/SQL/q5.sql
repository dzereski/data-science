SELECT
    name,
    monthlymaintenance,
    CASE
        WHEN monthlymaintenance > 100 THEN 'expensive'
        ELSE 'cheap'
    END as facility_label
FROM facilities
ORDER BY monthlymaintenance DESC;