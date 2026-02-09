"""
Демонстрация системы топ-списков Netta
"""

from netta import Netta, TopLists
import json
import os

def demo_top_lists():
    """Демонстрация топ-списков"""
    print("\n" + "="*80)
    print("ДЕМОНСТРАЦИЯ: ТОП-СПИСКИ NETTA")
    print("="*80)
    
    # Создаем тестовое приложение
    app = Netta()
    
    # Очищаем тестовые данные
    if os.path.exists('test_users.json'):
        os.remove('test_users.json')
    if os.path.exists('test_posts.json'):
        os.remove('test_posts.json')
    
    app.users_file = 'test_users.json'
    app.posts_file = 'test_posts.json'
    
    # Создаем тестовых пользователей
    print("\n1. 🧪 СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ")
    print("-"*40)
    
    test_users = [
        ("admin", True, True, 25),
        ("alex_pro", False, True, 15),
        ("maria_creative", False, True, 12),
        ("ivan_writer", False, True, 8),
        ("dmitry_tech", True, True, 5),
        ("olga_designer", False, False, 3),
        ("sophia_art", False, False, 2),
    ]
    
    for username, is_admin, is_verified, post_count in test_users:
        user = app.users.get(username)
        if not user:
            user = app.users[username] = type('obj', (object,), {
                'username': username,
                'is_admin': is_admin,
                'is_verified': is_verified,
                'posts': [],
                'followers': [],
                'stats': {},
                'reputation_score': 0
            })()
        
        # Добавляем тестовые посты
        for i in range(post_count):
            post = type('obj', (object,), {
                'id': f"post_{username}_{i}",
                'author': username,
                'author_verified': is_verified,
                'author_admin': is_admin,
                'content': f"Тестовый пост #{i} от {username} #Netta #тест",
                'likes': ['user1', 'user2', 'user3'] * (i + 1),
                'comments': [{'user': 'user1', 'text': 'Отлично!'}] * i,
                'shares': i,
                'views': 100 * (i + 1),
                'timestamp': '2024-01-15 10:00:00',
                'get_popularity_score': lambda: len(self.likes) * 2 + len(self.comments) * 3 + self.shares * 5,
                'display_compact': lambda: print(f"Пост от {self.author}")
            })()
            post.likes = ['user1', 'user2', 'user3'] * (i + 1)
            post.comments = [{'user': 'user1', 'text': 'Отлично!'}] * i
            post.shares = i
            
            app.all_posts.append(post)
            user.posts.append({'id': post.id})
    
    print(f"✅ Создано {len(app.users)} пользователей")
    print(f"✅ Создано {len(app.all_posts)} постов")
    
    # Тестируем TopLists
    print("\n2. 📊 ТЕСТИРОВАНИЕ TOPLISTS")
    print("-"*40)
    
    toplists = TopLists()
    
    # Топ администраторы
    print("\n👑 ТОП АДМИНИСТРАТОРЫ:")
    top_admins = toplists.get_top_admins(app.users)
    for username, post_count in top_admins:
        user = app.users.get(username)
        badge = "🔴" if user.is_admin else ""
        print(f"   {username} {badge} - {post_count} постов")
    
    # Топ авторы
    print("\n🏆 ТОП АВТОРЫ:")
    top_authors = toplists.get_top_authors(app.users)
    for username, score, post_count in top_authors[:5]:
        user = app.users.get(username)
        badge = "🔵" if user.is_verified else ("🔴" if user.is_admin else "👤")
        print(f"   {username} {badge} - {post_count} постов, {score} очков")
    
    # Популярные посты
    print("\n🔥 ПОПУЛЯРНЫЕ ПОСТЫ:")
    popular_posts = toplists.get_popular_posts(app.all_posts)
    for i, post in enumerate(popular_posts[:3], 1):
        print(f"   {i}. {post.author} - {post.get_popularity_score():.1f} очков")
    
    # Трендовые теги
    print("\n📍 ТРЕНДОВЫЕ ТЕГИ:")
    trending_tags = toplists.get_trending_tags(app.all_posts)
    for tag, count in trending_tags:
        print(f"   #{tag} - {count} упоминаний")
    
    # Демонстрация главной панели
    print("\n3. 🎨 ГЛАВНАЯ ПАНЕЛЬ NETTA")
    print("-"*40)
    print("""
    ┌─────────────────────────────────────────────────────────────┐
    │                    🐦 ГЛАВНАЯ ПАНЕЛЬ NETTA 🐦              │
    └─────────────────────────────────────────────────────────────┘
    
    👑 ТОП АДМИНИСТРАТОРЫ          🔥 ПОПУЛЯРНЫЕ ПОСТЫ
    ═════════════════════          ═════════════════════
    1. admin 🔴                   1. alex_pro - 150 очков
       📝 25 постов                 📝 "Только что прошел..."
       ⭐ Высокая репутация         ❤️ 50 | 💬 25 | 🔄 10
    
    2. dmitry_tech 🔴            2. maria_creative - 120 очков
       📝 5 постов                  📝 "Делитесь своими..."
       ⭐ Средняя репутация         ❤️ 40 | 💬 20 | 🔄 8
    
    🏆 ТОП АВТОРЫ                  🆕 НЕДАВНО ОПУБЛИКОВАННЫЕ
    ═════════════════════          ═════════════════════
    1. alex_pro 🔵                1. sophia_art 👤 (5 мин назад)
       📝 15 постов, 450 очков      📝 "Искусство объединяет..."
       ❤️ 225 лайков                ❤️ 12 | 💬 3
    
    2. maria_creative 🔵         2. olga_designer 👤 (15 мин назад)
       📝 12 постов, 360 очков      📝 "Дизайн - это искусство..."
       ❤️ 180 лайков                ❤️ 18 | 💬 6
    
    🔥 ТРЕНДОВЫЕ ТЕГИ              📊 СТАТИСТИКА ПЛАТФОРМЫ
    ═════════════════════          ═════════════════════
    #Netta - 15 упоминаний        👥 Пользователей: 7
    #верификация - 8 упоминаний   📝 Всего постов: 70
    #творчество - 5 упоминаний    ❤️ Всего лайков: 525
    """)
    
    print("\n" + "="*80)
    print("КЛЮЧЕВЫЕ ПРЕИМУЩЕСТВА:")
    print("="*80)
    print("1. 🎯 МОТИВАЦИЯ - пользователи стремятся попасть в топ")
    print("2. 📊 ПРОЗРАЧНОСТЬ - понятные критерии попадания в топ")
    print("3. 🔄 АКТУАЛЬНОСТЬ - списки обновляются каждые 5 минут")
    print("4. ⭐ ПРИЗНАНИЕ - топ-авторы получают особый статус")
    print("5. 📈 СТАТИСТИКА - детальная аналитика платформы")
    print("6. 🔥 ТРЕНДЫ - выявление популярных тем в реальном времени")

def run_demo():
    """Запуск демонстрации"""
    print("\n" + "="*80)
    print("         NETTA - СИСТЕМА ТОП-СПИСКОВ         ")
    print("="*80)
    
    print("\n🎯 НОВЫЕ ФУНКЦИИ:")
    print("1. 👑 Топ администраторы по активности")
    print("2. 🏆 Топ авторы по популярности контента")
    print("3. 🔥 Популярные посты (24 часа)")
    print("4. 🆕 Недавно опубликованные посты")
    print("5. 📍 Трендовые хештеги")
    print("6. 📊 Детальная статистика платформы")
    print("7. 🎨 Главная панель с обзором")
    
    while True:
        print("\n" + "="*40)
        print("1. Демонстрация топ-списков")
        print("2. Запуск основного приложения")
        print("3. Выход")
        
        choice = input("\nВыберите: ").strip()
        
        if choice == '1':
            demo_top_lists()
        elif choice == '2':
            print("\n🚀 Запуск Netta...")
            app = Netta()
            app.run()
            break
        elif choice == '3':
            print("\n🐦 До свидания!")
            break
        else:
            print("❌ Неверный выбор!")

if __name__ == "__main__":
    run_demo()
