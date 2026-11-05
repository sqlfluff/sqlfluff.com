MODEL (
    name demo.orders,
    kind FULL
);

SELECT
    order_id,
    amount
from (values (1, 25), (2, 150)) as orders(order_id, amount)
where amount >= @VAR('minimum_amount');
