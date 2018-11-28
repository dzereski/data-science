SELECT
    DISTINCT members.memid,
    CONCAT(surname, ', ', firstname) as member_name,
    name as court_name
FROM Bookings JOIN Members ON bookings.memid=members.memid JOIN Facilities ON bookings.facid=facilities.facid
WHERE name like 'Tennis%' AND members.memid > 0
ORDER BY member_name;