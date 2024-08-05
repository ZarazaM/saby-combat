from saby_combat import db_engine
from sqlalchemy import text


def get_upgrades(upgrade_ids: list[str] = None):

    with db_engine.connect() as connection:
        query_text = 'SELECT * FROM upgrades'
        if upgrade_ids is not None:
            if all(value.isdigit() for value in upgrade_ids):
                query_text += f'WHERE id IN ({", ".join(upgrade_ids)})'
            else:
                return {'message': 'Incorrect request, ids are not numeric'}

        query = text(query_text)
        result = connection.execute(query)
        return {'data': [row._asdict() for row in result]}


def delete_upgrades(upgrade_ids: list[str]):

    if all(value.isdigit() for value in upgrade_ids):
        with db_engine.connect() as connection:
            query = text(f'DELETE FROM upgrades WHERE id IN ({", ".join(upgrade_ids)}) RETURNING *')
            result = connection.execute(query)
            connection.commit()
            return {'message': 'deleted successfully', 'data': [row._asdict() for row in result]}

    return {'message': 'Incorrect request, ids are not numeric'}


def patch_upgrades(upgrade_modification: dict[str, any]):

    valid_fields = {'id', 'upgrade_name', 'upgrade_image', 'base_cost', 'coins_per_second', 'cost_multiplier'}
    invalid_fields = set(upgrade_modification.keys()) - valid_fields
    # TODO проверять значения на подходящесть
    if not invalid_fields:
        with db_engine.connect() as connection:
            upgrade_id = upgrade_modification.pop('id')
            updates = ', '.join([f'{key} = :{key}' for key in upgrade_modification.keys()])
            query = text(f'UPDATE upgrades SET {updates} WHERE id = {upgrade_id} RETURNING *')
            result = connection.execute(query, upgrade_modification)
            connection.commit()
            return {'message': 'updated successfully', 'data': [row._asdict() for row in result]}
    return {'message': f'Incorrect request, invalid parameters: {", ".join(invalid_fields)}'}


def create_upgrades(upgrade: dict[str, any]):

    valid_fields = {'upgrade_name', 'upgrade_image', 'base_cost', 'coins_per_second', 'cost_multiplier'}
    invalid_fields = set(upgrade.keys()) - valid_fields
    # TODO проверять значения на подходящесть
    if not invalid_fields:
        with db_engine.connect() as connection:
            columns = ', '.join(upgrade.keys())
            placeholders = ', '.join([':' + key for key in upgrade.keys()])
            query = text(f'INSERT INTO upgrades({columns}) '
                         f'VALUES ({placeholders}) RETURNING *')
            result = connection.execute(query, upgrade)
            connection.commit()
            return {'message': 'created successfully', 'data': [row._asdict() for row in result]}
    return {'message': f'Incorrect request, invalid parameters: {", ".join(invalid_fields)}'}


def get_user_upgrades(user_id: str = None, upgrade_id: str = None):

    with db_engine.connect() as connection:
        query_text = (f'SELECT *, CAST(up.base_cost*POWER(CAST(up.cost_multiplier AS FLOAT)/CAST(100 AS FLOAT)+1, user_upgrades.quantity) AS BIGINT) as purchase_cost FROM user_upgrades '
                      f'JOIN (SELECT * FROM upgrades) as up ON (user_upgrades.upgrade_id = up.id)')
        if user_id is not None and user_id.isdigit() and upgrade_id is not None and upgrade_id.isdigit():
            query_text += f'WHERE user_upgrades.user_id = {user_id} AND user_upgrades.upgrade_id = {upgrade_id}'
        elif user_id is not None and user_id.isdigit():
            query_text += f'WHERE user_upgrades.user_id = {user_id}'
        query = text(query_text)
        result = connection.execute(query)
        return {'data': [row._asdict() for row in result]}


def delete_user_upgrades(user_id: str = None, upgrade_id: str = None):

    if user_id is not None and user_id.isdigit() and upgrade_id is not None and upgrade_id.isdigit():
        with db_engine.connect() as connection:
            query = text(f'DELETE FROM user_upgrades WHERE user_id = {user_id} AND upgrade_id = {upgrade_id} RETURNING *')
            result = connection.execute(query)
            connection.commit()
            return {'message': 'entry deleted', 'data': [row._asdict() for row in result]}

    return {'message': 'Incorrect request, ids are not numeric'}


def patch_user_upgrades(modification: dict[str, any]):

    valid_fields = {'user_id', 'upgrade_id', 'quantity'}
    invalid_fields = set(modification) - valid_fields
    if not invalid_fields and (set(modification) & valid_fields) == valid_fields:
        with db_engine.connect() as connection:
            query = text(f'UPDATE user_upgrades SET quantity = {modification["quantity"]} WHERE user_id = {modification["user_id"]} AND upgrade_id = {modification["upgrade_id"]} RETURNING *')
            result = connection.execute(query)
            connection.commit()
            return {'message': 'successfully updated', 'data': [row._asdict() for row in result]}
    return {'message': f'Incorrect request, invalid parameters: {", ".join(invalid_fields)}'}


def purchase_user_upgrades(user_id: str = None, upgrade_id: str = None):

    if user_id is not None and user_id.isdigit() and upgrade_id is not None and upgrade_id.isdigit():
        with db_engine.connect() as connection:
            select_query = text(
                f'SELECT user_coins.user_id, user_coins.current_coins, us_up.quantity, up.base_cost, up.cost_multiplier, up.upgrade_name, up.coins_per_second FROM user_coins '
                f'JOIN(SELECT * FROM user_upgrades WHERE upgrade_id = {upgrade_id}) as us_up ON(user_coins.user_id = us_up.user_id) '
                f'JOIN(SELECT * FROM upgrades) as up ON(us_up.upgrade_id = up.id)'
                f'WHERE(user_coins.user_id = {user_id})')
            result = connection.execute(select_query).first()
            if result.current_coins >= result.base_cost * (result.cost_multiplier / 100 + 1) ** result.quantity:
                update_quantity_query = text(
                    f'UPDATE user_upgrades SET quantity = {result.quantity + 1} WHERE (user_id = {user_id} AND upgrade_id = {upgrade_id})')
                quantity_result = connection.execute(update_quantity_query)
                update_coins_query = text(
                    f'UPDATE user_coins SET coins_per_second = {result.coins_per_second}, current_coins = {result.current_coins - result.base_cost * (result.cost_multiplier / 100 + 1) ** result.quantity} WHERE user_id = {user_id}')
                coins_result = connection.execute(update_coins_query)
                connection.commit()
                return {'message': f'Upgrade "{result.upgrade_name}" purchased by user with id {result.user_id} for {result.base_cost * (result.cost_multiplier / 100 + 1) ** result.quantity}'}
            return {'message': 'Недостаточно средств для осуществления покупки'}
    return {'message': 'Incorrect request, ids are not numeric'}
