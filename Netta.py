import json
import os
import hashlib
import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

class Post:
    """Класс для постов"""
    def __init__(self, content: str, author: str, author_verified: bool = False, author_admin: bool = False):
        self.id = str(uuid.uuid4())[:8]
        self.content = content[:280]
        self.author = author
        self.author_verified = author_verified
        self.author_admin = author_admin
        self.timestamp = datetime.now()
        self.likes = []
        self.comments = []
        self.shares = 0
        self.views = 0
        self.tags = []
        self.is_pinned = False
        self.is_sponsored = False  # Рекламный пост
        
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author': self.author,
            'author_verified': self.author_verified,
            'author_admin': self.author_admin,
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'likes': self.likes,
            'comments': self.comments,
            'shares': self.shares,
            'views': self.views,
            'tags': self.tags,
            'is_pinned': self.is_pinned,
            'is_sponsored': self.is_sponsored
        }
    
    def display_compact(self):
        """Компактное отображение поста для ленты"""
        badge = self.get_author_badge()
        time_diff = self.get_time_diff()
        
        # Извлекаем хештеги
        content_preview = self.content
        if len(content_preview) > 100:
            content_preview = content_preview[:97] + "..."
        
        print(f"\n📝 {self.author} {badge}")
        print(f"   ⏰ {time_diff}")
        print(f"   {content_preview}")
        print(f"   ❤️ {len(self.likes)} | 💬 {len(self.comments)} | 🔄 {self.shares} | 👁️ {self.views}")
        
    def get_author_badge(self):
        """Получить значок автора"""
        if self.author_admin:
            return "🔴"
        elif self.author_verified:
            return "🔵"
        return ""
    
    def get_time_diff(self):
        """Получить разницу во времени"""
        now = datetime.now()
        diff = now - self.timestamp
        
        if diff.days > 365:
            years = diff.days // 365
            return f"{years} год назад" if years == 1 else f"{years} лет назад"
        elif diff.days > 30:
            months = diff.days // 30
            return f"{months} мес. назад"
        elif diff.days > 0:
            return f"{diff.days} дн. назад"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} ч. назад"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} мин. назад"
        else:
            return "только что"
    
    def get_popularity_score(self):
        """Оценка популярности поста"""
        return (len(self.likes) * 2 + len(self.comments) * 3 + self.shares * 5 + self.views * 0.1)

class TopLists:
    """Класс для управления топ-списками"""
    
    @staticmethod
    def get_top_admins(users: Dict[str, 'NettaUser'], limit: int = 5) -> List[Tuple[str, int]]:
        """Топ администраторов по активности"""
        admins = [(username, user) for username, user in users.items() if user.is_admin]
        
        # Сортируем по количеству постов
        sorted_admins = sorted(
            admins,
            key=lambda x: len(x[1].posts),
            reverse=True
        )
        
        return [(username, len(user.posts)) for username, user in sorted_admins[:limit]]
    
    @staticmethod
    def get_top_authors(users: Dict[str, 'NettaUser'], limit: int = 10) -> List[Tuple[str, int]]:
        """Топ авторов по популярности постов"""
        authors = []
        
        for username, user in users.items():
            if not user.posts:
                continue
                
            total_likes = 0
            total_comments = 0
            total_shares = 0
            
            for post_data in user.posts:
                # В реальном приложении здесь был бы доступ к объектам Post
                total_likes += len(post_data.get('likes', []))
                total_comments += len(post_data.get('comments', []))
                total_shares += post_data.get('shares', 0)
            
            popularity_score = total_likes * 2 + total_comments * 3 + total_shares * 5
            authors.append((username, popularity_score, len(user.posts)))
        
        # Сортируем по популярности
        sorted_authors = sorted(
            authors,
            key=lambda x: x[1],
            reverse=True
        )
        
        return [(username, score, posts_count) for username, score, posts_count in sorted_authors[:limit]]
    
    @staticmethod
    def get_popular_posts(posts: List['Post'], limit: int = 10) -> List['Post']:
        """Популярные посты (по лайкам, комментариям, шейрам)"""
        # Фильтруем слишком старые посты (не старше 30 дней)
        month_ago = datetime.now() - timedelta(days=30)
        recent_posts = [post for post in posts if post.timestamp > month_ago]
        
        # Сортируем по популярности
        sorted_posts = sorted(
            recent_posts,
            key=lambda post: post.get_popularity_score(),
            reverse=True
        )
        
        return sorted_posts[:limit]
    
    @staticmethod
    def get_recent_posts(posts: List['Post'], limit: int = 10) -> List['Post']:
        """Недавно опубликованные посты"""
        sorted_posts = sorted(
            posts,
            key=lambda post: post.timestamp,
            reverse=True
        )
        
        return sorted_posts[:limit]
    
    @staticmethod
    def get_trending_tags(posts: List['Post'], limit: int = 5) -> List[Tuple[str, int]]:
        """Трендовые хештеги"""
        tag_counts = defaultdict(int)
        
        for post in posts:
            # Извлекаем хештеги из текста
            words = post.content.split()
            hashtags = [word[1:].lower() for word in words if word.startswith('#') and len(word) > 1]
            
            for tag in hashtags:
                tag_counts[tag] += 1
        
        # Сортируем по частоте
        sorted_tags = sorted(
            tag_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_tags[:limit]

class VerificationRequest:
    """Запрос на верификацию"""
    def __init__(self, user_id: str, username: str):
        self.request_id = str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.username = username
        self.submitted_at = datetime.now()
        self.video_link = ""
        self.video_duration = 0
        self.status = "pending"
        self.reviewed_by = ""
        self.reviewed_at = None
        self.rejection_reason = ""
        self.notes = ""
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'username': self.username,
            'submitted_at': self.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
            'video_link': self.video_link,
            'video_duration': self.video_duration,
            'status': self.status,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.strftime("%Y-%m-%d %H:%M:%S") if self.reviewed_at else None,
            'rejection_reason': self.rejection_reason,
            'notes': self.notes
        }
    
    def display(self, detailed: bool = False):
        """Отображение запроса"""
        status_icons = {
            'pending': '⏳',
            'reviewing': '🔍',
            'approved': '✅',
            'rejected': '❌'
        }
        
        icon = status_icons.get(self.status, '📋')
        status_text = {
            'pending': 'Ожидает рассмотрения',
            'reviewing': 'На рассмотрении',
            'approved': 'Одобрено',
            'rejected': 'Отклонено'
        }
        
        print(f"\n{icon} Заявка #{self.request_id}")
        print(f"👤 Пользователь: {self.username}")
        print(f"📅 Дата подачи: {self.submitted_at.strftime('%d.%m.%Y %H:%M')}")
        print(f"📊 Статус: {status_text.get(self.status, self.status)}")
        
        if detailed:
            if self.video_duration:
                print(f"🎥 Длительность видео: {self.video_duration} сек.")
            if self.status == 'approved':
                print(f"✅ Одобрено: {self.reviewed_by}")
                print(f"📅 Дата одобрения: {self.reviewed_at.strftime('%d.%m.%Y %H:%M') if self.reviewed_at else 'Нет данных'}")
            elif self.status == 'rejected':
                print(f"❌ Причина отказа: {self.rejection_reason}")
                print(f"📅 Дата решения: {self.reviewed_at.strftime('%d.%m.%Y %H:%M') if self.reviewed_at else 'Нет данных'}")

class NettaUser:
    def __init__(self, username: str, email: str, password: str, is_admin: bool = False, is_verified: bool = False):
        # Генерируем уникальный цифровой ID
        self.user_id = self.generate_user_id()
        self.username = username
        self.email = email
        self.password = hashlib.sha256(password.encode()).hexdigest()
        self.is_admin = is_admin
        self.is_verified = is_verified
        self.created_at = datetime.now()
        self.last_login = None
        self.last_activity = datetime.now()
        
        # Профиль
        self.bio = "Привет! Я новый пользователь Netta! 🐦"
        self.location = ""
        self.website = ""
        self.avatar_color = self.generate_avatar_color()
        
        # Социальные связи
        self.posts = []
        self.followers = []
        self.following = []
        self.notifications = []
        self.messages = []
        self.verification_requests = []
        
        # Настройки
        self.theme = "light"
        self.privacy = "public"
        self.muted_users = []
        self.blocked_users = []
        
        # Статистика
        self.stats = {
            'total_posts': 0,
            'total_likes': 0,
            'total_comments': 0,
            'total_shares': 0,
            'total_views': 0,
            'total_followers': 0,
            'total_following': 0,
            'account_age_days': 0,
            'daily_posts': 0,
            'weekly_posts': 0,
            'monthly_posts': 0
        }
        
        # Верификация
        self.has_verification_button = True
        self.last_verification_request = None
        
        # Рейтинг
        self.reputation_score = 0
        self.is_featured = False  # Выделенный автор
    
    def generate_user_id(self) -> str:
        """Генерация уникального цифрового ID"""
        timestamp = int(datetime.now().timestamp() * 1000)
        random_num = random.randint(1000, 9999)
        return f"{timestamp}{random_num}"
    
    def generate_avatar_color(self) -> str:
        """Генерация цвета для аватара"""
        colors = ['#1DA1F2', '#FF6B6B', '#4ECDC4', '#FFD166', '#06D6A0', '#118AB2', '#EF476F', '#073B4C']
        return random.choice(colors)
    
    def get_short_id(self) -> str:
        """Получить короткий ID"""
        return f"ID:{self.user_id[:8]}..."
    
    def update_stats(self):
        """Обновление статистики"""
        self.stats['total_followers'] = len(self.followers)
        self.stats['total_following'] = len(self.following)
        self.stats['total_posts'] = len(self.posts)
        
        # Считаем лайки и комментарии
        total_likes = 0
        total_comments = 0
        total_shares = 0
        total_views = 0
        
        for post_data in self.posts:
            total_likes += len(post_data.get('likes', []))
            total_comments += len(post_data.get('comments', []))
            total_shares += post_data.get('shares', 0)
            total_views += post_data.get('views', 0)
        
        self.stats['total_likes'] = total_likes
        self.stats['total_comments'] = total_comments
        self.stats['total_shares'] = total_shares
        self.stats['total_views'] = total_views
        
        # Возраст аккаунта в днях
        age = datetime.now() - self.created_at
        self.stats['account_age_days'] = age.days
        
        # Обновляем репутацию
        self.reputation_score = (
            self.stats['total_posts'] * 10 +
            self.stats['total_likes'] * 2 +
            self.stats['total_comments'] * 3 +
            self.stats['total_shares'] * 5 +
            self.stats['total_followers'] * 20
        )
        
        if self.is_verified:
            self.reputation_score += 1000
        if self.is_admin:
            self.reputation_score += 5000
    
    def to_dict(self):
        """Преобразование в словарь для сохранения"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'is_admin': self.is_admin,
            'is_verified': self.is_verified,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'last_login': self.last_login.strftime("%Y-%m-%d %H:%M:%S") if self.last_login else None,
            'last_activity': self.last_activity.strftime("%Y-%m-%d %H:%M:%S"),
            'bio': self.bio,
            'location': self.location,
            'website': self.website,
            'avatar_color': self.avatar_color,
            'posts': self.posts,
            'followers': self.followers,
            'following': self.following,
            'theme': self.theme,
            'privacy': self.privacy,
            'muted_users': self.muted_users,
            'blocked_users': self.blocked_users,
            'has_verification_button': self.has_verification_button,
            'last_verification_request': self.last_verification_request.strftime("%Y-%m-%d %H:%M:%S") if self.last_verification_request else None,
            'stats': self.stats,
            'reputation_score': self.reputation_score,
            'is_featured': self.is_featured
        }
    
    def display_profile(self, detailed: bool = False):
        """Отображение профиля пользователя"""
        verification_badge = self.get_verification_badge()
        
        print(f"\n{'═'*60}")
        print(f"👤 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ")
        print(f"{'═'*60}")
        print(f"🏷️  Имя: {self.username} {verification_badge}")
        print(f"🔢 ID: {self.get_short_id()}")
        
        if self.is_featured:
            print(f"🌟 Выделенный автор")
        
        print(f"\n📝 Биография: {self.bio}")
        
        if self.location:
            print(f"📍 Местоположение: {self.location}")
        if self.website:
            print(f"🌐 Веб-сайт: {self.website}")
        
        print(f"\n📅 Зарегистрирован: {self.created_at.strftime('%d.%m.%Y')}")
        print(f"   (Аккаунту {self.stats['account_age_days']} дней)")
        
        if self.last_login:
            print(f"📱 Последний вход: {self.last_login.strftime('%d.%m.%Y %H:%M')}")
        
        print(f"\n👥 Подписчиков: {self.stats['total_followers']:,} | Подписок: {self.stats['total_following']:,}")
        print(f"📊 Постов: {self.stats['total_posts']:,} | Лайков: {self.stats['total_likes']:,}")
        print(f"💬 Комментариев: {self.stats['total_comments']:,} | Репостов: {self.stats['total_shares']:,}")
        
        if detailed:
            print(f"\n📈 Репутация: {self.reputation_score:,} очков")
            print(f"👁️  Просмотры: {self.stats['total_views']:,}")
            print(f"⚙️  Настройки:")
            print(f"   🎨 Тема: {'Светлая' if self.theme == 'light' else 'Тёмная'}")
            print(f"   🔒 Приватность: {'Публичный' if self.privacy == 'public' else 'Приватный'}")
        
        # Кнопка верификации
        if not self.is_verified and self.has_verification_button:
            print(f"\n{'═'*60}")
            print(f"✅ КНОПКА ВЕРИФИКАЦИИ ДОСТУПНА")
            print(f"   Получите синюю галочку! 🔵")
        
        print(f"{'═'*60}")
    
    def get_verification_badge(self):
        """Получить значок верификации"""
        if self.is_admin:
            return "🔴 [Администратор]"
        elif self.is_verified:
            return "🔵 [Верифицирован]"
        return ""

class Netta:
    def __init__(self):
        self.users_file = 'netta_users.json'
        self.verification_file = 'netta_verification.json'
        self.posts_file = 'netta_posts.json'
        self.current_user = None
        self.users = self.load_users()
        self.verification_requests = self.load_verification_requests()
        self.all_posts = self.load_posts()
        self.toplists = TopLists()
        
        # Кэширование топ-списков
        self.cache_top_lists = {}
        self.cache_expiry = datetime.now()
    
    def load_users(self) -> Dict[str, NettaUser]:
        """Загрузка пользователей из файла"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    users = {}
                    
                    for username, user_data in data.items():
                        user = NettaUser(
                            username=user_data['username'],
                            email=user_data['email'],
                            password="",
                            is_admin=user_data['is_admin'],
                            is_verified=user_data['is_verified']
                        )
                        
                        # Восстанавливаем все атрибуты
                        user.user_id = user_data['user_id']
                        user.password = user_data['password']
                        user.created_at = datetime.strptime(user_data['created_at'], "%Y-%m-%d %H:%M:%S")
                        
                        if user_data.get('last_login'):
                            user.last_login = datetime.strptime(user_data['last_login'], "%Y-%m-%d %H:%M:%S")
                        
                        if user_data.get('last_activity'):
                            user.last_activity = datetime.strptime(user_data['last_activity'], "%Y-%m-%d %H:%M:%S")
                        
                        user.bio = user_data['bio']
                        user.location = user_data.get('location', '')
                        user.website = user_data.get('website', '')
                        user.avatar_color = user_data.get('avatar_color', '#1DA1F2')
                        user.posts = user_data.get('posts', [])
                        user.followers = user_data.get('followers', [])
                        user.following = user_data.get('following', [])
                        user.theme = user_data.get('theme', 'light')
                        user.privacy = user_data.get('privacy', 'public')
                        user.muted_users = user_data.get('muted_users', [])
                        user.blocked_users = user_data.get('blocked_users', [])
                        user.has_verification_button = user_data.get('has_verification_button', True)
                        
                        if user_data.get('last_verification_request'):
                            user.last_verification_request = datetime.strptime(
                                user_data['last_verification_request'], 
                                "%Y-%m-%d %H:%M:%S"
                            )
                        
                        user.stats = user_data.get('stats', {
                            'total_posts': 0,
                            'total_likes': 0,
                            'total_comments': 0,
                            'total_shares': 0,
                            'total_views': 0,
                            'total_followers': 0,
                            'total_following': 0,
                            'account_age_days': 0,
                            'daily_posts': 0,
                            'weekly_posts': 0,
                            'monthly_posts': 0
                        })
                        
                        user.reputation_score = user_data.get('reputation_score', 0)
                        user.is_featured = user_data.get('is_featured', False)
                        
                        user.update_stats()
                        users[username] = user
                    
                    return users
            except Exception as e:
                print(f"Ошибка загрузки пользователей: {e}")
                return {}
        return {}
    
    def load_posts(self) -> List[Post]:
        """Загрузка всех постов"""
        posts = []
        
        # Сначала пробуем загрузить из отдельного файла
        if os.path.exists(self.posts_file):
            try:
                with open(self.posts_file, 'r', encoding='utf-8') as f:
                    posts_data = json.load(f)
                    
                    for post_data in posts_data:
                        post = Post(
                            post_data['content'],
                            post_data['author'],
                            post_data.get('author_verified', False),
                            post_data.get('author_admin', False)
                        )
                        post.id = post_data['id']
                        post.timestamp = datetime.strptime(post_data['timestamp'], "%Y-%m-%d %H:%M:%S")
                        post.likes = post_data.get('likes', [])
                        post.comments = post_data.get('comments', [])
                        post.shares = post_data.get('shares', 0)
                        post.views = post_data.get('views', 0)
                        post.tags = post_data.get('tags', [])
                        post.is_pinned = post_data.get('is_pinned', False)
                        post.is_sponsored = post_data.get('is_sponsored', False)
                        posts.append(post)
            except:
                pass
        
        # Если файла нет или ошибка, собираем посты из пользователей
        if not posts:
            for user in self.users.values():
                for post_data in user.posts:
                    post = Post(
                        post_data['content'],
                        post_data['author'],
                        post_data.get('author_verified', False),
                        post_data.get('author_admin', False)
                    )
                    post.id = post_data['id']
                    post.timestamp = datetime.strptime(post_data['timestamp'], "%Y-%m-%d %H:%M:%S")
                    post.likes = post_data.get('likes', [])
                    post.comments = post_data.get('comments', [])
                    post.shares = post_data.get('shares', 0)
                    post.views = post_data.get('views', 0)
                    post.tags = post_data.get('tags', [])
                    post.is_pinned = post_data.get('is_pinned', False)
                    post.is_sponsored = post_data.get('is_sponsored', False)
                    posts.append(post)
        
        return posts
    
    def load_verification_requests(self) -> Dict[str, VerificationRequest]:
        """Загрузка запросов на верификацию"""
        if os.path.exists(self.verification_file):
            try:
                with open(self.verification_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    requests = {}
                    
                    for req_id, req_data in data.items():
                        req = VerificationRequest(req_data['user_id'], req_data['username'])
                        req.request_id = req_data['request_id']
                        req.submitted_at = datetime.strptime(req_data['submitted_at'], "%Y-%m-%d %H:%M:%S")
                        req.video_link = req_data['video_link']
                        req.video_duration = req_data['video_duration']
                        req.status = req_data['status']
                        req.reviewed_by = req_data['reviewed_by']
                        
                        if req_data['reviewed_at']:
                            req.reviewed_at = datetime.strptime(req_data['reviewed_at'], "%Y-%m-%d %H:%M:%S")
                        
                        req.rejection_reason = req_data['rejection_reason']
                        req.notes = req_data['notes']
                        
                        requests[req_id] = req
                    
                    return requests
            except:
                return {}
        return {}
    
    def save_users(self):
        """Сохранение пользователей"""
        data = {username: user.to_dict() for username, user in self.users.items()}
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_posts(self):
        """Сохранение всех постов"""
        posts_data = [post.to_dict() for post in self.all_posts]
        with open(self.posts_file, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, ensure_ascii=False, indent=2)
    
    def save_verification_requests(self):
        """Сохранение запросов на верификацию"""
        data = {req.request_id: req.to_dict() for req in self.verification_requests.values()}
        with open(self.verification_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_top_lists(self):
        """Получение всех топ-списков (с кэшированием)"""
        # Проверяем, не устарел ли кэш
        if datetime.now() - self.cache_expiry < timedelta(minutes=5) and self.cache_top_lists:
            return self.cache_top_lists
        
        print("\n🔄 Обновление топ-списков...")
        
        # Получаем все списки
        top_admins = self.toplists.get_top_admins(self.users)
        top_authors = self.toplists.get_top_authors(self.users)
        popular_posts = self.toplists.get_popular_posts(self.all_posts)
        recent_posts = self.toplists.get_recent_posts(self.all_posts)
        trending_tags = self.toplists.get_trending_tags(self.all_posts)
        
        # Кэшируем результаты
        self.cache_top_lists = {
            'top_admins': top_admins,
            'top_authors': top_authors,
            'popular_posts': popular_posts,
            'recent_posts': recent_posts,
            'trending_tags': trending_tags
        }
        self.cache_expiry = datetime.now()
        
        return self.cache_top_lists
    
    def display_main_dashboard(self):
        """Главная панель с топ-списками"""
        print("\n" + "="*80)
        print("                  🐦 ГЛАВНАЯ ПАНЕЛЬ NETTA 🐦                  ")
        print("="*80)
        
        # Получаем топ-списки
        top_lists = self.get_top_lists()
        
        # Левый столбец: Топ администраторы и авторы
        print("\n" + "═"*40)
        print("👑 ТОП АДМИНИСТРАТОРЫ")
        print("═"*40)
        
        if top_lists['top_admins']:
            for i, (username, posts_count) in enumerate(top_lists['top_admins'][:5], 1):
                user = self.users.get(username)
                if user:
                    badge = "🔴"
                    print(f"{i}. {username} {badge}")
                    print(f"   📝 Постов: {posts_count:,} | 👥 Подписчиков: {len(user.followers):,}")
                    print(f"   ⭐ Репутация: {user.reputation_score:,}")
                    if i < len(top_lists['top_admins']):
                        print()
        else:
            print("Пока нет активных администраторов")
        
        print("\n" + "═"*40)
        print("🏆 ТОП АВТОРЫ")
        print("═"*40)
        
        if top_lists['top_authors']:
            for i, (username, score, posts_count) in enumerate(top_lists['top_authors'][:5], 1):
                user = self.users.get(username)
                if user:
                    badge = "🔵" if user.is_verified else "👤"
                    print(f"{i}. {username} {badge}")
                    print(f"   📝 Постов: {posts_count:,} | 📈 Очки: {score:,}")
                    print(f"   ❤️ Лайков: {user.stats['total_likes']:,}")
                    if i < len(top_lists['top_authors'][:5]):
                        print()
        else:
            print("Пока нет активных авторов")
        
        print("\n" + "═"*40)
        print("🔥 ТРЕНДОВЫЕ ТЕГИ")
        print("═"*40)
        
        if top_lists['trending_tags']:
            for i, (tag, count) in enumerate(top_lists['trending_tags'], 1):
                print(f"#{tag} - {count} упоминаний")
        else:
            print("Пока нет трендовых тегов")
        
        # Правый столбец: Популярные и свежие посты
        print("\n" + "="*80)
        print("🔥 ПОПУЛЯРНЫЕ ПОСТЫ (24 часа)")
        print("="*80)
        
        if top_lists['popular_posts']:
            for i, post in enumerate(top_lists['popular_posts'][:3], 1):
                print(f"\n{i}. {'📌' if post.is_pinned else '🔥'}")
                post.display_compact()
                print()
        else:
            print("\nПока нет популярных постов")
        
        print("\n" + "="*80)
        print("🆕 НЕДАВНО ОПУБЛИКОВАННЫЕ")
        print("="*80)
        
        if top_lists['recent_posts']:
            for i, post in enumerate(top_lists['recent_posts'][:5], 1):
                print(f"\n{i}. {'📌' if post.is_pinned else '🆕'}")
                post.display_compact()
        else:
            print("\nПока нет недавних постов")
        
        # Статистика платформы
        print("\n" + "="*80)
        print("📊 СТАТИСТИКА ПЛАТФОРМЫ")
        print("="*80)
        
        total_users = len(self.users)
        total_posts = len(self.all_posts)
        total_likes = sum(len(post.likes) for post in self.all_posts)
        total_comments = sum(len(post.comments) for post in self.all_posts)
        
        # Активные пользователи (за последние 7 дней)
        week_ago = datetime.now() - timedelta(days=7)
        active_users = sum(1 for user in self.users.values() 
                          if user.last_activity and user.last_activity > week_ago)
        
        # Новые пользователи (за последние 7 дней)
        new_users = sum(1 for user in self.users.values() 
                       if user.created_at > week_ago)
        
        print(f"👥 Пользователей: {total_users:,}")
        print(f"📝 Всего постов: {total_posts:,}")
        print(f"❤️ Всего лайков: {total_likes:,}")
        print(f"💬 Всего комментариев: {total_comments:,}")
        print(f"🎯 Активных пользователей (7 дней): {active_users:,}")
        print(f"🚀 Новых пользователей (7 дней): {new_users:,}")
        
        print(f"\n{'='*80}")
    
    def show_extended_top_lists(self):
        """Расширенные топ-списки"""
        while True:
            print("\n" + "="*80)
            print("📈 РАСШИРЕННЫЕ ТОП-СПИСКИ")
            print("="*80)
            
            top_lists = self.get_top_lists()
            
            print("\n1. 👑 Топ администраторы (полный список)")
            print("2. 🏆 Топ авторы (полный список)")
            print("3. 🔥 Популярные посты (все)")
            print("4. 🆕 Все свежие посты")
            print("5. 🔍 Поиск по трендам")
            print("6. 📊 Подробная статистика")
            print("7. ↩️ Назад в главное меню")
            
            choice = input("\n🎯 Выберите раздел: ").strip()
            
            if choice == '1':
                self.show_full_top_admins(top_lists['top_admins'])
            elif choice == '2':
                self.show_full_top_authors(top_lists['top_authors'])
            elif choice == '3':
                self.show_all_popular_posts(top_lists['popular_posts'])
            elif choice == '4':
                self.show_all_recent_posts(top_lists['recent_posts'])
            elif choice == '5':
                self.trend_search()
            elif choice == '6':
                self.show_detailed_stats()
            elif choice == '7':
                break
            else:
                print("❌ Неверный выбор!")
    
    def show_full_top_admins(self, top_admins):
        """Полный список топ администраторов"""
        print("\n" + "="*80)
        print("👑 ПОЛНЫЙ СПИСОК АДМИНИСТРАТОРОВ")
        print("="*80)
        
        if not top_admins:
            print("На платформе пока нет администраторов")
            return
        
        for i, (username, posts_count) in enumerate(top_admins, 1):
            user = self.users.get(username)
            if user:
                print(f"\n{i}. {username} 🔴")
                print(f"   🔢 ID: {user.get_short_id()}")
                print(f"   📝 Постов: {posts_count:,}")
                print(f"   👥 Подписчиков: {len(user.followers):,}")
                print(f"   📅 На платформе: {user.stats['account_age_days']} дней")
                print(f"   ⭐ Репутация: {user.reputation_score:,}")
                print(f"   📧 Email: {user.email}")
                
                # Последняя активность
                if user.last_activity:
                    hours_ago = (datetime.now() - user.last_activity).seconds // 3600
                    if hours_ago < 24:
                        print(f"   🕐 Активен: {hours_ago} часов назад")
                    else:
                        days_ago = (datetime.now() - user.last_activity).days
                        print(f"   🕐 Активен: {days_ago} дней назад")
        
        input("\nНажмите Enter для продолжения...")
    
    def show_full_top_authors(self, top_authors):
        """Полный список топ авторов"""
        print("\n" + "="*80)
        print("🏆 ПОЛНЫЙ СПИСОК ТОП АВТОРОВ")
        print("="*80)
        
        if not top_authors:
            print("На платформе пока нет активных авторов")
            return
        
        print("\n📋 Формат: Место | Автор | Посты | Очки | Статус")
        print("-"*80)
        
        for i, (username, score, posts_count) in enumerate(top_authors, 1):
            user = self.users.get(username)
            if user:
                badge = "🔵" if user.is_verified else ("🔴" if user.is_admin else "👤")
                status = "Верифицирован" if user.is_verified else ("Админ" if user.is_admin else "Обычный")
                
                print(f"{i:2}. {username:20} {badge} | 📝 {posts_count:4,} | ⭐ {score:8,} | {status}")
                
                if i % 10 == 0 and i < len(top_authors):
                    input("\nПродолжить? (Enter)...")
        
        print("\n" + "="*80)
        print("💡 Советы для попадания в топ:")
        print("   • Регулярно публикуйте интересный контент")
        print("   • Взаимодействуйте с другими пользователями")
        print("   • Используйте хештеги для увеличения охвата")
        print("   • Пройдите верификацию для повышения доверия")
        
        input("\nНажмите Enter для продолжения...")
    
    def show_all_popular_posts(self, popular_posts):
        """Все популярные посты"""
        print("\n" + "="*80)
        print("🔥 ВСЕ ПОПУЛЯРНЫЕ ПОСТЫ")
        print("="*80)
        
        if not popular_posts:
            print("Пока нет популярных постов")
            return
        
        print("📊 Сортировка по популярности (лайки ×2 + комментарии ×3 + репосты ×5)")
        print("-"*80)
        
        for i, post in enumerate(popular_posts, 1):
            print(f"\n{i}. {'📌' if post.is_pinned else '🔥'} ПОПУЛЯРНОСТЬ: {post.get_popularity_score():.1f}")
            print(f"   👤 Автор: {post.author} {'🔵' if post.author_verified else ('🔴' if post.author_admin else '👤')}")
            print(f"   ⏰ {post.get_time_diff()}")
            print(f"   {post.content[:100]}{'...' if len(post.content) > 100 else ''}")
            print(f"   ❤️ {len(post.likes)} | 💬 {len(post.comments)} | 🔄 {post.shares} | 👁️ {post.views}")
            
            if post.tags:
                print(f"   📍 Теги: {', '.join(['#' + tag for tag in post.tags])}")
            
            if i % 5 == 0 and i < len(popular_posts):
                action = input("\n[Enter - дальше, M - меню]: ").strip().upper()
                if action == 'M':
                    break
        
        input("\nНажмите Enter для продолжения...")
    
    def show_all_recent_posts(self, recent_posts):
        """Все свежие посты"""
        print("\n" + "="*80)
        print("🆕 ВСЕ СВЕЖИЕ ПОСТЫ")
        print("="*80)
        
        if not recent_posts:
            print("Пока нет свежих постов")
            return
        
        # Группируем посты по дням
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        today_posts = []
        yesterday_posts = []
        older_posts = []
        
        for post in recent_posts:
            post_date = post.timestamp.date()
            if post_date == today:
                today_posts.append(post)
            elif post_date == yesterday:
                yesterday_posts.append(post)
            else:
                older_posts.append(post)
        
        # Выводим посты
        if today_posts:
            print(f"\n📅 СЕГОДНЯ ({today.strftime('%d.%m.%Y')}):")
            for i, post in enumerate(today_posts, 1):
                print(f"\n  {i}. {post.author}: {post.content[:80]}...")
                print(f"     ⏰ {post.timestamp.strftime('%H:%M')} | ❤️ {len(post.likes)}")
        
        if yesterday_posts:
            print(f"\n📅 ВЧЕРА ({yesterday.strftime('%d.%m.%Y')}):")
            for i, post in enumerate(yesterday_posts, 1):
                print(f"\n  {i}. {post.author}: {post.content[:80]}...")
                print(f"     ⏰ {post.timestamp.strftime('%H:%M')} | ❤️ {len(post.likes)}")
        
        if older_posts:
            print(f"\n📅 РАНЕЕ:")
            for i, post in enumerate(older_posts[:10], 1):
                date_str = post.timestamp.strftime('%d.%m')
                print(f"\n  {i}. [{date_str}] {post.author}: {post.content[:80]}...")
                print(f"     ❤️ {len(post.likes)} | 💬 {len(post.comments)}")
        
        input("\nНажмите Enter для продолжения...")
    
    def trend_search(self):
        """Поиск по трендам"""
        print("\n" + "="*80)
        print("🔍 ПОИСК ПО ТРЕНДАМ")
        print("="*80)
        
        top_lists = self.get_top_lists()
        trending_tags = top_lists['trending_tags']
        
        print("\n🔥 АКТУАЛЬНЫЕ ТРЕНДЫ:")
        for i, (tag, count) in enumerate(trending_tags, 1):
            print(f"{i}. #{tag} - {count} упоминаний")
        
        print("\n🎯 ВЫБЕРИТЕ ДЕЙСТВИЕ:")
        print("1. 🔍 Поиск по тегу")
        print("2. 📊 Статистика тега")
        print("3. 👥 Авторы тега")
        print("4. ↩️ Назад")
        
        choice = input("\nВыберите: ").strip()
        
        if choice == '1':
            tag = input("Введите тег (без #): ").strip().lower()
            self.search_by_tag(tag)
        elif choice == '2':
            if trending_tags:
                tag_num = input(f"Номер тега (1-{len(trending_tags)}): ").strip()
                if tag_num.isdigit():
                    idx = int(tag_num) - 1
                    if 0 <= idx < len(trending_tags):
                        tag = trending_tags[idx][0]
                        self.show_tag_stats(tag)
            else:
                tag = input("Введите тег (без #): ").strip().lower()
                self.show_tag_stats(tag)
        elif choice == '3':
            if trending_tags:
                tag_num = input(f"Номер тега (1-{len(trending_tags)}): ").strip()
                if tag_num.isdigit():
                    idx = int(tag_num) - 1
                    if 0 <= idx < len(trending_tags):
                        tag = trending_tags[idx][0]
                        self.show_tag_authors(tag)
            else:
                tag = input("Введите тег (без #): ").strip().lower()
                self.show_tag_authors(tag)
    
    def search_by_tag(self, tag: str):
        """Поиск постов по тегу"""
        posts_with_tag = []
        
        for post in self.all_posts:
            # Простой поиск тега в тексте
            if f"#{tag}" in post.content.lower() or tag in [t.lower() for t in post.tags]:
                posts_with_tag.append(post)
        
        print(f"\n🔍 РЕЗУЛЬТАТЫ ПО ТЕГУ #{tag}:")
        print(f"📊 Найдено постов: {len(posts_with_tag)}")
        
        if posts_with_tag:
            # Сортируем по популярности
            sorted_posts = sorted(posts_with_tag, key=lambda p: p.get_popularity_score(), reverse=True)
            
            for i, post in enumerate(sorted_posts[:10], 1):
                print(f"\n{i}. {post.author} ({post.get_time_diff()})")
                print(f"   {post.content[:100]}...")
                print(f"   ❤️ {len(post.likes)} | 💬 {len(post.comments)}")
        
        input("\nНажмите Enter для продолжения...")
    
    def show_tag_stats(self, tag: str):
        """Статистика по тегу"""
        posts_with_tag = []
        authors = set()
        total_likes = 0
        total_comments = 0
        
        for post in self.all_posts:
            if f"#{tag}" in post.content.lower() or tag in [t.lower() for t in post.tags]:
                posts_with_tag.append(post)
                authors.add(post.author)
                total_likes += len(post.likes)
                total_comments += len(post.comments)
        
        print(f"\n📊 СТАТИСТИКА ТЕГА #{tag}:")
        print(f"📝 Всего постов: {len(posts_with_tag)}")
        print(f"👥 Уникальных авторов: {len(authors)}")
        print(f"❤️ Всего лайков: {total_likes}")
        print(f"💬 Всего комментариев: {total_comments}")
        
        if posts_with_tag:
            # Самый популярный пост
            most_popular = max(posts_with_tag, key=lambda p: p.get_popularity_score())
            print(f"\n🔥 САМЫЙ ПОПУЛЯРНЫЙ ПОСТ:")
            print(f"   Автор: {most_popular.author}")
            print(f"   Время: {most_popular.get_time_diff()}")
            print(f"   Популярность: {most_popular.get_popularity_score():.1f}")
            
            # Активность по дням
            from collections import defaultdict
            daily_counts = defaultdict(int)
            
            for post in posts_with_tag:
                date_str = post.timestamp.strftime('%d.%m')
                daily_counts[date_str] += 1
            
            print(f"\n📅 АКТИВНОСТЬ ПО ДНЯМ:")
            for date_str, count in sorted(daily_counts.items(), reverse=True)[:7]:
                print(f"   {date_str}: {count} постов")
        
        input("\nНажмите Enter для продолжения...")
    
    def show_tag_authors(self, tag: str):
        """Авторы, использующие тег"""
        author_counts = defaultdict(int)
        author_likes = defaultdict(int)
        
        for post in self.all_posts:
            if f"#{tag}" in post.content.lower() or tag in [t.lower() for t in post.tags]:
                author_counts[post.author] += 1
                author_likes[post.author] += len(post.likes)
        
        if not author_counts:
            print(f"\n😞 Никто не использовал тег #{tag}")
            return
        
        print(f"\n👥 АВТОРЫ ТЕГА #{tag}:")
        
        # Сортируем авторов по количеству постов
        sorted_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
        
        for i, (author, count) in enumerate(sorted_authors[:10], 1):
            user = self.users.get(author)
            badge = "🔵" if user and user.is_verified else ("🔴" if user and user.is_admin else "👤")
            likes = author_likes[author]
            
            print(f"{i}. {author} {badge}")
            print(f"   📝 Постов с тегом: {count}")
            print(f"   ❤️ Лайков: {likes}")
            
            if user:
                print(f"   📊 Всего постов: {user.stats['total_posts']}")
        
        input("\nНажмите Enter для продолжения...")
    
    def show_detailed_stats(self):
        """Подробная статистика платформы"""
        print("\n" + "="*80)
        print("📊 ПОДРОБНАЯ СТАТИСТИКА ПЛАТФОРМЫ")
        print("="*80)
        
        total_users = len(self.users)
        total_posts = len(self.all_posts)
        total_likes = sum(len(post.likes) for post in self.all_posts)
        total_comments = sum(len(post.comments) for post in self.all_posts)
        total_shares = sum(post.shares for post in self.all_posts)
        total_views = sum(post.views for post in self.all_posts)
        
        # Активные пользователи
        now = datetime.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        active_today = sum(1 for user in self.users.values() 
                          if user.last_activity and user.last_activity > day_ago)
        active_week = sum(1 for user in self.users.values() 
                         if user.last_activity and user.last_activity > week_ago)
        active_month = sum(1 for user in self.users.values() 
                          if user.last_activity and user.last_activity > month_ago)
        
        # Новые пользователи
        new_today = sum(1 for user in self.users.values() 
                       if user.created_at > day_ago)
        new_week = sum(1 for user in self.users.values() 
                      if user.created_at > week_ago)
        new_month = sum(1 for user in self.users.values() 
                       if user.created_at > month_ago)
        
        # Верифицированные пользователи
        verified_users = sum(1 for user in self.users.values() if user.is_verified)
        admin_users = sum(1 for user in self.users.values() if user.is_admin)
        
        # Статистика постов
        posts_today = sum(1 for post in self.all_posts if post.timestamp > day_ago)
        posts_week = sum(1 for post in self.all_posts if post.timestamp > week_ago)
        posts_month = sum(1 for post in self.all_posts if post.timestamp > month_ago)
        
        print(f"\n👥 ПОЛЬЗОВАТЕЛИ:")
        print(f"   Всего: {total_users:,}")
        print(f"   🔵 Верифицированных: {verified_users:,} ({verified_users/total_users*100:.1f}%)")
        print(f"   🔴 Администраторов: {admin_users:,}")
        print(f"   🎯 Активных сегодня: {active_today:,}")
        print(f"   🎯 Активных за неделю: {active_week:,}")
        print(f"   🎯 Активных за месяц: {active_month:,}")
        
        print(f"\n📝 ПОСТЫ:")
        print(f"   Всего: {total_posts:,}")
        print(f"   Сегодня: {posts_today:,}")
        print(f"   За неделю: {posts_week:,}")
        print(f"   За месяц: {posts_month:,}")
        
        print(f"\n📊 ВЗАИМОДЕЙСТВИЯ:")
        print(f"   ❤️ Лайков: {total_likes:,}")
        print(f"   💬 Комментариев: {total_comments:,}")
        print(f"   🔄 Репостов: {total_shares:,}")
        print(f"   👁️ Просмотров: {total_views:,}")
        
        print(f"\n🚀 РОСТ:")
        print(f"   Новых сегодня: {new_today:,}")
        print(f"   Новых за неделю: {new_week:,}")
        print(f"   Новых за месяц: {new_month:,}")
        
        # Средние показатели
        if total_users > 0:
            avg_posts = total_posts / total_users
            avg_likes = total_likes / total_posts if total_posts > 0 else 0
            avg_comments = total_comments / total_posts if total_posts > 0 else 0
            
            print(f"\n📈 СРЕДНИЕ ПОКАЗАТЕЛИ:")
            print(f"   Постов на пользователя: {avg_posts:.1f}")
            print(f"   Лайков на пост: {avg_likes:.1f}")
            print(f"   Комментариев на пост: {avg_comments:.1f}")
        
        # Топ 5 самых активных дней
        from collections import defaultdict
        daily_post_counts = defaultdict(int)
        
        for post in self.all_posts:
            date_str = post.timestamp.strftime('%d.%m.%Y')
            daily_post_counts[date_str] += 1
        
        if daily_post_counts:
            top_days = sorted(daily_post_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            print(f"\n📅 ТОП-5 САМЫХ АКТИВНЫХ ДНЕЙ:")
            for date_str, count in top_days:
                print(f"   {date_str}: {count} постов")
        
        input("\nНажмите Enter для продолжения...")
    
    def create_post(self):
        """Создание поста с тегами"""
        if not self.current_user:
            print("❌ Сначала войдите в систему!")
            return
        
        print("\n" + "="*80)
        print("📝 СОЗДАНИЕ НОВОГО ПОСТА")
        print("="*80)
        
        print("\n💡 Советы:")
        print("   • Используйте #хештеги для увеличения охвата")
        print("   • Упоминайте @пользователей")
        print("   • Максимум 280 символов")
        print("   • Теги помогут попасть в тренды")
        
        content = input("\nЧто у вас нового?\n").strip()
        
        if not content:
            print("❌ Пост не может быть пустым!")
            return
        
        if len(content) > 280:
            print(f"⚠️ Пост сокращен до 280 символов (было {len(content)})")
            content = content[:280]
        
        # Извлекаем теги
        words = content.split()
        tags = [word[1:].lower() for word in words if word.startswith('#') and len(word) > 1]
        
        # Создаем пост
        post = Post(
            content,
            self.current_user.username,
            self.current_user.is_verified,
            self.current_user.is_admin
        )
        post.tags = tags
        
        # Увеличиваем счетчик просмотров у авторов, которых упомянули
        mentions = [word[1:] for word in words if word.startswith('@') and len(word) > 1]
        for mention in mentions:
            if mention in self.users and mention != self.current_user.username:
                # Отправляем уведомление (в реальном приложении)
                print(f"📢 Упоминание @{mention}")
        
        # Добавляем пост
        self.current_user.posts.append(post.to_dict())
        self.current_user.stats['total_posts'] += 1
        self.all_posts.append(post)
        
        # Обновляем активность
        self.current_user.last_activity = datetime.now()
        
        # Очищаем кэш топ-списков
        self.cache_top_lists = {}
        
        self.save_users()
        self.save_posts()
        
        print("✅ Пост опубликован!")
        
        if tags:
            print(f"📌 Использованы теги: {', '.join(['#' + tag for tag in tags])}")
            print("💡 Ваш пост может появиться в трендах!")
        
        # Предлагаем сделать пост закрепленным
        if len(self.current_user.posts) == 1:
            choice = input("\n📌 Закрепить этот пост в профиле? (да/нет): ").strip().lower()
            if choice in ['да', 'д', 'y', 'yes']:
                post.is_pinned = True
                print("✅ Пост закреплен!")
    
    def run(self):
        """Запуск приложения"""
        print("\n" + "="*80)
        print("          🐦 ДОБРО ПОЖАЛОВАТЬ В NETTA! 🐦          ")
        print("="*80)
        print("Социальная сеть с топ-авторами и системой верификации")
        
        # Создаем тестовых пользователей, если их нет
        self.create_test_data()
        
        # Главное меню
        while True:
            if not self.current_user:
                self.show_main_menu()
            else:
                self.show_user_menu()
    
    def create_test_data(self):
        """Создание тестовых данных"""
        # Администратор по умолчанию
        if 'admin' not in self.users:
            admin = NettaUser('admin', 'admin@netta.social', 'admin123', is_admin=True, is_verified=True)
            admin.bio = "👑 Главный администратор Netta"
            admin.avatar_color = '#FF0000'
            self.users['admin'] = admin
        
        # Тестовые пользователи
        test_users = [
            ('alex_pro', 'alex@netta.social', 'pass123', False, True),
            ('maria_creative', 'maria@netta.social', 'pass123', False, True),
            ('ivan_writer', 'ivan@netta.social', 'pass123', False, True),
            ('olga_designer', 'olga@netta.social', 'pass123', False, False),
            ('dmitry_tech', 'dmitry@netta.social', 'pass123', True, True),
            ('sophia_art', 'sophia@netta.social', 'pass123', False, False),
        ]
        
        for username, email, password, is_admin, is_verified in test_users:
            if username not in self.users:
                user = NettaUser(username, email, password, is_admin, is_verified)
                user.bio = f"Тестовый пользователь Netta | Люблю общаться!"
                self.users[username] = user
        
        # Тестовые посты
        if len(self.all_posts) < 20:
            test_posts = [
                ("admin", "Добро пожаловать в Netta! 🐦 Новая социальная сеть с системой верификации и топ-авторами! #Netta #новое #соцсеть", True, True),
                ("alex_pro", "Только что прошел верификацию! Получил синюю галочку 🔵 Процесс занял всего 3 дня! #верификация #галочка #успех", False, True),
                ("maria_creative", "Делитесь своими творческими работами! Netta - идеальная платформа для креативных людей! #творчество #арт #дизайн", False, True),
                ("ivan_writer", "Пишите посты, делитесь мыслями, находите единомышленников! Каждый может стать топ-автором! #писательство #блог #автор", False, True),
                ("dmitry_tech", "Технологии будущего уже здесь! Netta использует современные алгоритмы для рекомендаций контента. #технологии #инновации #будущее", True, True),
                ("olga_designer", "Дизайн - это искусство! Показываю свои последние работы. Что думаете? #дизайн #искусство #креатив", False, False),
                ("sophia_art", "Искусство объединяет людей! В Netta нашел много интересных художников. #искусство #художники #сообщество", False, False),
                ("admin", "Топ-авторы получают специальные значки и повышенную видимость! Стремитесь к вершинам! #топас #рейтинг #мотивация", True, True),
                ("alex_pro", "Как попасть в топ авторов? Регулярно публикуйте качественный контент и взаимодействуйте с сообществом! #советы #рост #развитие", False, True),
                ("maria_creative", "Новый проект готов! Скоро покажу всем в Netta. Следите за обновлениями! #новыйпроект #анонс #скоро", False, True),
            ]
            
            for author, content, is_admin, is_verified in test_posts:
                if author in self.users:
                    post = Post(content, author, is_verified, is_admin)
                    # Добавляем случайные лайки и комментарии
                    for _ in range(random.randint(5, 50)):
                        post.likes.append(f"user{random.randint(1, 100)}")
                    for _ in range(random.randint(2, 20)):
                        post.comments.append({"user": f"user{random.randint(1, 100)}", "text": "Отличный пост!"})
                    post.shares = random.randint(0, 15)
                    post.views = random.randint(50, 500)
                    
                    self.all_posts.append(post)
                    self.users[author].posts.append(post.to_dict())
        
        self.save_users()
        self.save_posts()
    
    def show_main_menu(self):
        """Главное меню (неавторизованный)"""
        print("\n" + "="*80)
        print("               ГЛАВНОЕ МЕНЮ NETTA               ")
        print("="*80)
        
        # Показываем топ-списки даже неавторизованным пользователям
        self.display_main_dashboard()
        
        print("\n🎯 ОСНОВНЫЕ ДЕЙСТВИЯ:")
        print("1. 📝 Регистрация")
        print("2. 🔐 Вход в аккаунт")
        print("3. 📈 Расширенные топ-списки")
        print("4. 🔍 Поиск пользователей")
        print("5. ℹ️ О системе")
        print("6. 🚪 Выход")
        
        choice = input("\n🎯 Выберите действие: ").strip()
        
        if choice == '1':
            self.register()
        elif choice == '2':
            self.login()
        elif choice == '3':
            self.show_extended_top_lists()
        elif choice == '4':
            self.search_users()
        elif choice == '5':
            self.show_system_info()
        elif choice == '6':
            print("\n🐦 До новых встреч в Netta!")
            exit()
        else:
            print("❌ Неверный выбор!")
    
    def show_user_menu(self):
        """Меню пользователя (авторизованный)"""
        # Обновляем статистику
        self.current_user.update_stats()
        self.current_user.last_login = datetime.now()
        self.current_user.last_activity = datetime.now()
        
        badge = "🔴" if self.current_user.is_admin else ("🔵" if self.current_user.is_verified else "👤")
        
        print("\n" + "="*80)
        print(f"        ДОБРО ПОЖАЛОВАТЬ, {self.current_user.username} {badge}")
        print("="*80)
        print(f"🔢 Ваш ID: {self.current_user.get_short_id()}")
        print(f"📊 Постов: {self.current_user.stats['total_posts']} | Подписчиков: {self.current_user.stats['total_followers']}")
        print(f"⭐ Репутация: {self.current_user.reputation_score:,} очков")
        
        # Проверяем, в топе ли пользователь
        top_lists = self.get_top_lists()
        top_authors = [username for username, _, _ in top_lists['top_authors']]
        
        if self.current_user.username in top_authors:
            position = top_authors.index(self.current_user.username) + 1
            print(f"🏆 Вы в топе авторов! Место: {position}")
        
        # Показываем главную панель
        self.display_main_dashboard()
        
        print("\n" + "="*80)
        print("🎯 ВАШИ ДЕЙСТВИЯ:")
        print("1. 📝 Создать пост (попасть в тренды!)")
        print("2. 👤 Мой профиль")
        print("3. ✏️ Редактировать профиль")
        print("4. ✅ Верификация")
        print("5. 📰 Моя лента")
        print("6. 📈 Расширенные топ-списки")
        print("7. 🔍 Поиск пользователей")
        
        if self.current_user.is_admin:
            print("8. 👑 Панель администратора")
            print("9. 👨‍⚖️ Управление верификацией")
        
        print("0. 🔓 Выйти из аккаунта")
        
        choice = input("\n🎯 Выберите действие: ").strip()
        
        if choice == '1':
            self.create_post()
        elif choice == '2':
            self.current_user.display_profile(detailed=True)
            input("\nНажмите Enter для продолжения...")
        elif choice == '3':
            self.edit_profile()
        elif choice == '4':
            self.verification_system()
        elif choice == '5':
            self.show_feed()
        elif choice == '6':
            self.show_extended_top_lists()
        elif choice == '7':
            self.search_users()
        elif choice == '8' and self.current_user.is_admin:
            self.admin_panel()
        elif choice == '9' and self.current_user.is_admin:
            self.admin_verification_panel()
        elif choice == '0':
            self.current_user = None
            print("\n✅ Вы вышли из аккаунта")
        else:
            print("❌ Неверный выбор!")

# Добавьте недостающие методы (из предыдущих версий):

def search_users(self):
    """Поиск пользователей"""
    print("\n" + "="*80)
    print("🔍 ПОИСК ПОЛЬЗОВАТЕЛЕЙ")
    print("="*80)
    
    query = input("Введите имя пользователя или часть имени: ").strip().lower()
    
    if not query:
        print("❌ Введите запрос для поиска")
        return
    
    results = []
    for username, user in self.users.items():
        if query in username.lower() or query in user.bio.lower():
            results.append(user)
    
    if not results:
        print("😞 Пользователи не найдены")
        return
    
    print(f"\n📋 Найдено пользователей: {len(results)}")
    for i, user in enumerate(results[:10], 1):
        badge = "🔴" if user.is_admin else ("🔵" if user.is_verified else "👤")
        print(f"\n{i}. {user.username} {badge}")
        print(f"   📝 {user.bio[:50]}..." if user.bio else "   📝 Нет биографии")
        print(f"   📊 Постов: {user.stats['total_posts']} | Подписчиков: {len(user.followers)}")
        print(f"   ⭐ Репутация: {user.reputation_score:,}")
    
    choice = input("\nНомер для просмотра профиля (0 - назад): ").strip()
    if choice.isdigit():
        num = int(choice)
        if 1 <= num <= len(results):
            self.view_user_profile(results[num-1].username)

def verification_system(self):
    """Система верификации"""
    if not self.current_user:
        print("❌ Сначала войдите в систему!")
        return
    
    print("\n" + "="*80)
    print("          СИСТЕМА ВЕРИФИКАЦИИ          ")
    print("="*80)
    
    if self.current_user.is_verified:
        print("\n🎉 Вы уже верифицированы! 🔵")
        return
    
    # ... (остальной код верификации из предыдущей версии)

def show_feed(self):
    """Лента пользователя"""
    if not self.current_user:
        return
    
    print("\n" + "="*80)
    print("📰 ВАША ЛЕНТА")
    print("="*80)
    
    # Показываем посты от подписок
    following_posts = []
    for user in self.current_user.following:
        if user in self.users:
            following_posts.extend(self.users[user].posts)
    
    if not following_posts:
        print("Вы еще ни на кого не подписаны!")
        return
    
    # Сортируем по дате
    following_posts.sort(key=lambda x: x['timestamp'], reverse=True)
    
    for post_data in following_posts[:20]:
        # Находим объект Post
        post = next((p for p in self.all_posts if p.id == post_data['id']), None)
        if post:
            post.display_compact()
            print()

def show_system_info(self):
    """Информация о системе"""
    print("\n" + "="*80)
    print("          ИНФОРМАЦИЯ О NETTA          ")
    print("="*80)
    
    print("\n🎯 ОСОБЕННОСТИ СИСТЕМЫ:")
    print("• 🔢 Уникальные цифровые ID для каждого пользователя")
    print("• 🎥 Система верификации через видео 30-40 секунд")
    print("• 👑 Топ администраторы и авторы")
    print("• 🔥 Популярные и свежие посты")
    print("• 🔵 Синяя галочка - верифицированный")
    print("• 🔴 Красная галочка - администратор")
    
    print("\n📊 ТОП-СПИСКИ:")
    print("• Обновляются каждые 5 минут")
    print("• Учитывают активность за последние 30 дней")
    print("• Алгоритм: лайки ×2 + комментарии ×3 + репосты ×5")
    print("• Топ-авторы получают повышенную видимость")
    
    input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    app = Netta()
    app.run()
