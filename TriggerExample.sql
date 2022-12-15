create trigger PlaceProductOrder on dbo.app_productorder
after insert as
begin
insert into dbo.app_systemmessage (create_time, content, user_id, is_read)
values (GETDATE(),
        '（触发器）您的商品已卖出，请及时与买方联系。',
		(select seller_id from dbo.app_product where product_id = (select product_id from inserted)),
		0)
end