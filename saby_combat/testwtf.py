from saby_combat import db_engine
from sqlalchemy import text
with (db_engine.connect() as conn):
        result_1 = conn.execute(text("SELECT ROW_NUMBER() OVER(ORDER BY user_coins.total_coins DESC), "
                            "CONCAT(users.surname, ' ', users.name, ' ', users.patronymic), user_coins.total_coins "
                            "FROM users JOIN user_coins ON users.id = user_coins.user_id "
                            "ORDER BY user_coins.total_coins DESC LIMIT 100"))

        result_2 = conn.execute(text("SELECT ROW_NUMBER() OVER(ORDER BY user_coins.click_count DESC), "
                                     "CONCAT(users.surname, ' ', users.name, ' ', users.patronymic), user_coins.click_count "
                                     "FROM users JOIN user_coins ON users.id = user_coins.user_id "
                                     "ORDER BY user_coins.click_count DESC LIMIT 100"))

        result_3s = conn.execute(text("SELECT ROW_NUMBER() OVER(ORDER BY SUM(user_coins.total_coins) DESC), "
                                      "clans.clan_name, SUM(user_coins.total_coins) "
                                      "FROM user_coins JOIN users ON user_coins.user_id = users.id "
                                      "JOIN clans ON users.clan_id = clans.id "
                                      "GROUP BY clans.id "
                                      "ORDER BY SUM(user_coins.total_coins) DESC LIMIT 100"))
        result_help = []
        result_3 = []
        for row in result_3s:
            k = row[2]
            k = int(k)
            result_help = list((row[0], row[1], k))
            result_3.append(result_help)
        for row in result_3:
            print(row[0], row[1], row[2])

        result_4 = conn.execute(text("SELECT ROW_NUMBER() OVER(ORDER BY SUM(user_coins.click_count) DESC), "
                                     "clans.clan_name, SUM(user_coins.click_count) "
                                     "FROM user_coins JOIN users ON user_coins.user_id = users.id "
                                     "JOIN clans ON users.clan_id = clans.id "
                                     "GROUP BY clans.id "
                                     "ORDER BY SUM(user_coins.click_count) DESC LIMIT 100"))
        print(result_4.all())