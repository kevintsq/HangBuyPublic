create trigger PlaceProductOrder on dbo.app_productorder
after insert as
begin
insert into dbo.app_systemmessage (create_time, content, user_id, is_read)
values (GETDATE(),
        '����������������Ʒ���������뼰ʱ������ϵ��',
		(select seller_id from dbo.app_product where product_id = (select product_id from inserted)),
		0)
end