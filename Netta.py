#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════╗
║                    🐦 NETTA - Социальная сеть                  ║
║                      Версия 1.0                                ║
╚═══════════════════════════════════════════════════════════════╝
"""

import sqlite3
import hashlib
import os
from datetime import datetime
import json

# ═══════════════════════════════════════════════════════════════
# 🎨 ЦВЕТА И СТИЛИ ДЛЯ КОНСОЛИ
# ═══════════════════════════════════════════════════════════════

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Галочки верификации
BLUE_CHECK = f"{Colors.BLUE}✓{Colors.END}"      # Верифицированный пользователь
RED_CHECK = f"{Colors.RED}✓{Colors.END}"        # Администратор
NO_CHECK = ""                                     # Без верификации

# ═══════════════════════════════════════════════════════════════
# 🗄️ БАЗА ДАННЫХ
# ═══════════════════════════════════════════════════════════════

class Database:
    def __init__(self, db_name="netta.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Инициализация таблиц базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                display_name TEXT,
                bio TEXT DEFAULT '',
                avatar TEXT DEFAULT '👤',
                location TEXT DEFAULT '',
                website TEXT DEFAULT '',
                verification_status INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                followers_count INTEGER DEFAULT 0,
                following_count INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица постов (neets)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS neets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                likes_count INTEGER DEFAULT 0,
                reneets_count INTEGER DEFAULT 0,
                replies_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Таблица подписок
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS follows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                follower_id INTEGER NOT NULL,
                following_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (follower_id) REFERENCES users(id),
                FOREIGN KEY (following_id) REFERENCES users(id),
                UNIQUE(follower_id, following_id)
            )
        ''')
        
        # Таблица лайков
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                neet_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (neet_id) REFERENCES neets(id),
                UNIQUE(user_id, neet_id)
            )
        ''')
        
        # Таблица заявок на верификацию
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()

# ═══════════════════════════════════════════════════════════════
# 👤 КЛАСС ПОЛЬЗОВАТЕЛЯ
# ═══════════════════════════════════════════════════════════════

class User:
    def __init__(self, db):
        self.db = db
        self.current_user = None
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username, email, password, display_name=None):
        """Регистрация нового пользователя"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = self.hash_password(password)
            display_name = display_name or username
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, display_name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, display_name))
            
            conn.commit()
            conn.close()
            return True, "✅ Регистрация успешна! Добро пожаловать в Netta!"
        
        except sqlite3.IntegrityError as e:
            conn.close()
            if 'username' in str(e):
                return False, "❌ Это имя пользователя уже занято!"
            elif 'email' in str(e):
                return False, "❌ Этот email уже зарегистрирован!"
            return False, f"❌ Ошибка регистрации: {e}"
    
    def login(self, username, password):
        """Авторизация пользователя"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            self.current_user = {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'display_name': user[4],
                'bio': user[5],
                'avatar': user[6],
                'location': user[7],
                'website': user[8],
                'verification_status': user[9],
                'is_admin': user[10],
                'created_at': user[11],
                'followers_count': user[12],
                'following_count': user[13]
            }
            return True, f"✅ Добро пожаловать, {self.current_user['display_name']}!"
        
        return False, "❌ Неверное имя пользователя или пароль!"
    
    def logout(self):
        """Выход из аккаунта"""
        self.current_user = None
        return True, "👋 До свидания! Вы вышли из аккаунта."
    
    def get_verification_badge(self, verification_status, is_admin):
        """Получить значок верификации"""
        if is_admin:
            return RED_CHECK
        elif verification_status == 1:
            return BLUE_CHECK
        return NO_CHECK
    
    def update_profile(self, **kwargs):
        """Обновление профиля"""
        if not self.current_user:
            return False, "❌ Вы не авторизованы!"
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        allowed_fields = ['display_name', 'bio', 'avatar', 'location', 'website']
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields and value:
                updates.append(f"{field} = ?")
                values.append(value)
                self.current_user[field] = value
        
        if updates:
            values.append(self.current_user['id'])
            cursor.execute(f'''
                UPDATE users SET {', '.join(updates)} WHERE id = ?
            ''', values)
            conn.commit()
        
        conn.close()
        return True, "✅ Профиль обновлен!"
    
    def get_profile(self, username=None):
        """Получить профиль пользователя"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if username:
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        elif self.current_user:
            cursor.execute('SELECT * FROM users WHERE id = ?', (self.current_user['id'],))
        else:
            conn.close()
            return None
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'display_name': user[4],
                'bio': user[5],
                'avatar': user[6],
                'location': user[7],
                'website': user[8],
                'verification_status': user[9],
                'is_admin': user[10],
                'created_at': user[11],
                'followers_count': user[12],
                'following_count': user[13]
            }
        return None
    
    def request_verification(self, reason):
        """Подать заявку на верификацию"""
        if not self.current_user:
            return False, "❌ Вы не авторизованы!"
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Проверяем, нет ли уже активной заявки
        cursor.execute('''
            SELECT * FROM verification_requests 
            WHERE user_id = ? AND status = 'pending'
        ''', (self.current_user['id'],))
        
        if cursor.fetchone():
            conn.close()
            return False, "❌ У вас уже есть активная заявка на верификацию!"
        
        cursor.execute('''
            INSERT INTO verification_requests (user_id, reason)
            VALUES (?, ?)
        ''', (self.current_user['id'], reason))
        
        conn.commit()
        conn.close()
        return True, "✅ Заявка на верификацию отправлена!"

# ═══════════════════════════════════════════════════════════════
# 📝 КЛАСС ПОСТОВ (NEETS)
# ═══════════════════════════════════════════════════════════════

class Neet:
    def __init__(self, db, user):
        self.db = db
        self.user = user
    
    def create(self, content):
        """Создание нового поста"""
        if not self.user.current_user:
            return False, "❌ Вы не авторизованы!"
        
        if len(content) > 280:
            return False, "❌ Пост не может быть длиннее 280 символов!"
        
        if not content.strip():
            return False, "❌ Пост не может быть пустым!"
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO neets (user_id, content) VALUES (?, ?)
        ''', (self.user.current_user['id'], content))
        
        conn.commit()
        conn.close()
        return True, "✅ Neet опубликован!"
    
    def get_feed(self, limit=20):
        """Получить ленту постов"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.*, u.username, u.display_name, u.avatar, 
                   u.verification_status, u.is_admin
            FROM neets n
            JOIN users u ON n.user_id = u.id
            ORDER BY n.created_at DESC
            LIMIT ?
        ''', (limit,))
        
        neets = cursor.fetchall()
        conn.close()
        
        return [{
            'id': n[0],
            'user_id': n[1],
            'content': n[2],
            'likes_count': n[3],
            'reneets_count': n[4],
            'replies_count': n[5],
            'created_at': n[6],
            'username': n[7],
            'display_name': n[8],
            'avatar': n[9],
            'verification_status': n[10],
            'is_admin': n[11]
        } for n in neets]
    
    def like(self, neet_id):
        """Поставить лайк"""
        if not self.user.current_user:
            return False, "❌ Вы не авторизованы!"
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO likes (user_id, neet_id) VALUES (?, ?)
            ''', (self.user.current_user['id'], neet_id))
            
            cursor.execute('''
                UPDATE neets SET likes_count = likes_count + 1 WHERE id = ?
            ''', (neet_id,))
            
            conn.commit()
            conn.close()
            return True, "❤️ Вам понравился этот Neet!"
        
        except sqlite3.IntegrityError:
            conn.close()
            return False, "❌ Вы уже лайкнули этот Neet!"
    
    def get_user_neets(self, user_id, limit=20):
        """Получить посты конкретного пользователя"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.*, u.username, u.display_name, u.avatar,
                   u.verification_status, u.is_admin
            FROM neets n
            JOIN users u ON n.user_id = u.id
            WHERE n.user_id = ?
            ORDER BY n.created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        neets = cursor.fetchall()
        conn.close()
        
        return [{
            'id': n[0],
            'user_id': n[1],
            'content': n[2],
            'likes_count': n[3],
            'reneets_count': n[4],
            'replies_count': n[5],
            'created_at': n[6],
            'username': n[7],
            'display_name': n[8],
            'avatar': n[9],
            'verification_status': n[10],
            'is_admin': n[11]
        } for n in neets]

# ═══════════════════════════════════════════════════════════════
# 🖥️ ИНТЕРФЕЙС ПРИЛОЖЕНИЯ
# ═══════════════════════════════════════════════════════════════

class NettaApp:
    def __init__(self):
        self.db = Database()
        self.user = User(self.db)
        self.neet = Neet(self.db, self.user)
    
    def clear_screen(self):
        """Очистка экрана"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Вывод заголовка"""
        print(f"""
{Colors.CYAN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     {Colors.BLUE}███╗   ██╗{Colors.WHITE}███████╗{Colors.CYAN}████████╗{Colors.BLUE}████████╗{Colors.WHITE} █████╗ {Colors.CYAN}           ║
║     {Colors.BLUE}████╗  ██║{Colors.WHITE}██╔════╝{Colors.CYAN}╚══██╔══╝{Colors.BLUE}╚══██╔══╝{Colors.WHITE}██╔══██╗{Colors.CYAN}           ║
║     {Colors.BLUE}██╔██╗ ██║{Colors.WHITE}█████╗  {Colors.CYAN}   ██║   {Colors.BLUE}   ██║   {Colors.WHITE}███████║{Colors.CYAN}           ║
║     {Colors.BLUE}██║╚██╗██║{Colors.WHITE}██╔══╝  {Colors.CYAN}   ██║   {Colors.BLUE}   ██║   {Colors.WHITE}██╔══██║{Colors.CYAN}           ║
║     {Colors.BLUE}██║ ╚████║{Colors.WHITE}███████╗{Colors.CYAN}   ██║   {Colors.BLUE}   ██║   {Colors.WHITE}██║  ██║{Colors.CYAN}           ║
║     {Colors.BLUE}╚═╝  ╚═══╝{Colors.WHITE}╚══════╝{Colors.CYAN}   ╚═╝   {Colors.BLUE}   ╚═╝   {Colors.WHITE}╚═╝  ╚═╝{Colors.CYAN}           ║
║                                                               ║
║                   🐦 Социальная сеть нового поколения          ║
╚═══════════════════════════════════════════════════════════════╝{Colors.END}
        """)
    
    def print_menu(self, options, title="Меню"):
        """Вывод меню"""
        print(f"\n{Colors.YELLOW}{'═' * 50}")
        print(f"  📋 {title}")
        print(f"{'═' * 50}{Colors.END}")
        
        for key, value in options.items():
            print(f"  {Colors.CYAN}[{key}]{Colors.END} {value}")
        
        print(f"{Colors.YELLOW}{'═' * 50}{Colors.END}")
    
    def display_neet(self, neet):
        """Отображение одного поста"""
        badge = self.user.get_verification_badge(
            neet['verification_status'], 
            neet['is_admin']
        )
        
        time_str = neet['created_at'][:16] if neet['created_at'] else 'Недавно'
        
        print(f"""
{Colors.WHITE}┌──────────────────────────────────────────────────────┐{Colors.END}
│ {neet['avatar']} {Colors.BOLD}{neet['display_name']}{Colors.END} {badge} {Colors.CYAN}@{neet['username']}{Colors.END}
│ {Colors.WHITE}{time_str}{Colors.END}
├──────────────────────────────────────────────────────┤
│ {neet['content'][:50]}
│ {neet['content'][50:100] if len(neet['content']) > 50 else ''}
├──────────────────────────────────────────────────────┤
│ {Colors.RED}❤️ {neet['likes_count']}{Colors.END}  🔄 {neet['reneets_count']}  💬 {neet['replies_count']}
{Colors.WHITE}└──────────────────────────────────────────────────────┘{Colors.END}
        """)
    
    def display_profile(self, profile):
        """Отображение профиля"""
        badge = self.user.get_verification_badge(
            profile['verification_status'],
            profile['is_admin']
        )
        
        badge_text = ""
        if profile['is_admin']:
            badge_text = f"{Colors.RED}[Администратор]{Colors.END}"
        elif profile['verification_status'] == 1:
            badge_text = f"{Colors.BLUE}[Верифицирован]{Colors.END}"
        
        print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                         👤 ПРОФИЛЬ                            ║
╠══════════════════════════════════════════════════════════════╣{Colors.END}
║
║   {profile['avatar']}  {Colors.BOLD}{profile['display_name']}{Colors.END} {badge} {badge_text}
║      {Colors.CYAN}@{profile['username']}{Colors.END}
║
║   📝 {profile['bio'] or 'Нет описания'}
║
║   📍 {profile['location'] or 'Не указано'}
║   🔗 {profile['website'] or 'Не указано'}
║
║   {Colors.GREEN}📊 {profile['followers_count']} подписчиков{Colors.END}  •  {Colors.BLUE}{profile['following_count']} подписок{Colors.END}
║
║   📅 Дата регистрации: {str(profile['created_at'])[:10]}
║
{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.END}
        """)
    
    def register_screen(self):
        """Экран регистрации"""
        self.clear_screen()
        print(f"\n{Colors.GREEN}{'═' * 50}")
        print("  📝 РЕГИСТРАЦИЯ В NETTA")
        print(f"{'═' * 50}{Colors.END}\n")
        
        username = input(f"{Colors.CYAN}👤 Имя пользователя: {Colors.END}").strip()
        email = input(f"{Colors.CYAN}📧 Email: {Colors.END}").strip()
        password = input(f"{Colors.CYAN}🔒 Пароль: {Colors.END}").strip()
        password_confirm = input(f"{Colors.CYAN}🔒 Подтвердите пароль: {Colors.END}").strip()
        display_name = input(f"{Colors.CYAN}📛 Отображаемое имя (Enter для пропуска): {Colors.END}").strip()
        
        if password != password_confirm:
            print(f"\n{Colors.RED}❌ Пароли не совпадают!{Colors.END}")
            input("\nНажмите Enter для продолжения...")
            return
        
        if len(password) < 6:
            print(f"\n{Colors.RED}❌ Пароль должен быть не менее 6 символов!{Colors.END}")
            input("\nНажмите Enter для продолжения...")
            return
        
        success, message = self.user.register(
            username, email, password, 
            display_name if display_name else None
        )
        
        print(f"\n{message}")
        input("\nНажмите Enter для продолжения...")
    
    def login_screen(self):
        """Экран входа"""
        self.clear_screen()
        print(f"\n{Colors.GREEN}{'═' * 50}")
        print("  🔐 ВХОД В NETTA")
        print(f"{'═' * 50}{Colors.END}\n")
        
        username = input(f"{Colors.CYAN}👤 Имя пользователя: {Colors.END}").strip()
        password = input(f"{Colors.CYAN}🔒 Пароль: {Colors.END}").strip()
        
        success, message = self.user.login(username, password)
        print(f"\n{message}")
        input("\nНажмите Enter для продолжения...")
    
    def edit_profile_screen(self):
        """Экран редактирования профиля"""
        self.clear_screen()
        print(f"\n{Colors.GREEN}{'═' * 50}")
        print("  ✏️ РЕДАКТИРОВАНИЕ ПРОФИЛЯ")
        print(f"{'═' * 50}{Colors.END}\n")
        
        print(f"{Colors.YELLOW}(Оставьте пустым, чтобы не менять){Colors.END}\n")
        
        display_name = input(f"{Colors.CYAN}📛 Новое имя: {Colors.END}").strip()
        bio = input(f"{Colors.CYAN}📝 О себе: {Colors.END}").strip()
        avatar = input(f"{Colors.CYAN}😀 Эмодзи-аватар: {Colors.END}").strip()
        location = input(f"{Colors.CYAN}📍 Местоположение: {Colors.END}").strip()
        website = input(f"{Colors.CYAN}🔗 Веб-сайт: {Colors.END}").strip()
        
        success, message = self.user.update_profile(
            display_name=display_name,
            bio=bio,
            avatar=avatar,
            location=location,
            website=website
        )
        
        print(f"\n{message}")
        input("\nНажмите Enter для продолжения...")
    
    def create_neet_screen(self):
        """Экран создания поста"""
        self.clear_screen()
        print(f"\n{Colors.GREEN}{'═' * 50}")
        print("  ✍️ НОВЫЙ NEET")
        print(f"{'═' * 50}{Colors.END}\n")
        
        print(f"{Colors.YELLOW}Максимум 280 символов{Colors.END}\n")
        
        content = input(f"{Colors.CYAN}📝 Что нового? {Colors.END}").strip()
        
        success, message = self.neet.create(content)
        print(f"\n{message}")
        input("\nНажмите Enter для продолжения...")
    
    def feed_screen(self):
        """Экран ленты"""
        self.clear_screen()
        print(f"\n{Colors.GREEN}{'═' * 50}")
        print("  📰 ЛЕНТА NETTA")
        print(f"{'═' * 50}{Colors.END}")
        
        neets = self.neet.get_feed()
        
        if not neets:
            print(f"\n{Colors.YELLOW}Пока нет постов. Будьте первым!{Colors.END}")
        else:
            for neet in neets:
                self.display_neet(neet)
        
        print(f"\n{Colors.YELLOW}Действия:{Colors.END}")
        print(f"  {Colors.CYAN}[L номер]{Colors.END} - Лайкнуть пост")
        print(f"  {Colors.CYAN}[B]{Colors.END} - Назад")
        
        action = input(f"\n{Colors.CYAN}Ваш выбор: {Colors.END}").strip().upper()
        
        if action.startswith('L '):
            try:
                neet_id = int(action.split()[1])
                success, message = self.neet.like(neet_id)
                print(f"\n{message}")
                input("\nНажмите Enter для продолжения...")
            except:
                pass
    
    def profile_screen(self):
        """Экран профиля"""
        self.clear_screen()
        
        profile = self.user.get_profile()
        if profile:
            self.display_profile(profile)
            
            # Показать посты пользователя
            print(f"\n{Colors.GREEN}📝 Ваши Neets:{Colors.END}")
            neets = self.neet.get_user_neets(profile['id'])
            
            if neets:
                for neet in neets[:5]:
                    self.display_neet(neet)
            else:
                print(f"\n{Colors.YELLOW}У вас пока нет постов{Colors.END}")
        
        input("\nНажмите Enter для продолжения...")
    
    def verification_request_screen(self):
        """Экран подачи заявки на верификацию"""
        self.clear_screen()
        print(f"\n{Colors.BLUE}{'═' * 50}")
        print(f"  {BLUE_CHECK} ЗАЯВКА НА ВЕРИФИКАЦИЮ")
        print(f"{'═' * 50}{Colors.END}\n")
        
        print(f"""
{Colors.WHITE}Верификация подтверждает подлинность вашего аккаунта.

{Colors.BLUE}🔵 Синяя галочка{Colors.END} - для обычных пользователей
{Colors.RED}🔴 Красная галочка{Colors.END} - для администраторов

{Colors.YELLOW}Требования для верификации:{Colors.END}
• Активный аккаунт
• Заполненный профиль  
• Причина для верификации
        """)
        
        reason = input(f"\n{Colors.CYAN}📝 Почему вы хотите получить верификацию? {Colors.END}").strip()
        
        if reason:
            success, message = self.user.request_verification(reason)
            print(f"\n{message}")
        else:
            print(f"\n{Colors.RED}❌ Причина не может быть пустой!{Colors.END}")
        
        input("\nНажмите Enter для продолжения...")
    
    def view_user_screen(self):
        """Просмотр профиля другого пользователя"""
        self.clear_screen()
        print(f"\n{Colors.GREEN}{'═' * 50}")
        print("  🔍 ПОИСК ПОЛЬЗОВАТЕЛЯ")
        print(f"{'═' * 50}{Colors.END}\n")
        
        username = input(f"{Colors.CYAN}👤 Введите @username: {Colors.END}").strip().replace('@', '')
        
        profile = self.user.get_profile(username)
        
        if profile:
            self.display_profile(profile)
            
            # Показать посты пользователя
            print(f"\n{Colors.GREEN}📝 Neets пользователя:{Colors.END}")
            neets = self.neet.get_user_neets(profile['id'])
            
            if neets:
                for neet in neets[:5]:
                    self.display_neet(neet)
            else:
                print(f"\n{Colors.YELLOW}У этого пользователя пока нет постов{Colors.END}")
        else:
            print(f"\n{Colors.RED}❌ Пользователь не найден!{Colors.END}")
        
        input("\nНажмите Enter для продолжения...")
    
    def main_menu(self):
        """Главное меню (после авторизации)"""
        while self.user.current_user:
            self.clear_screen()
            self.print_header()
            
            badge = self.user.get_verification_badge(
                self.user.current_user['verification_status'],
                self.user.current_user['is_admin']
            )
            
            print(f"\n{Colors.GREEN}Вы вошли как: {Colors.BOLD}{self.user.current_user['display_name']}{Colors.END} {badge} {Colors.CYAN}@{self.user.current_user['username']}{Colors.END}")
            
            menu = {
                '1': '📰 Лента',
                '2': '✍️ Написать Neet',
                '3': '👤 Мой профиль',
                '4': '✏️ Редактировать профиль',
                '5': '🔍 Найти пользователя',
                '6': f'{BLUE_CHECK} Подать заявку на верификацию',
                '0': '🚪 Выйти'
            }
            
            self.print_menu(menu, "Главное меню")
            
            choice = input(f"\n{Colors.CYAN}Ваш выбор: {Colors.END}").strip()
            
            if choice == '1':
                self.feed_screen()
            elif choice == '2':
                self.create_neet_screen()
            elif choice == '3':
                self.profile_screen()
            elif choice == '4':
                self.edit_profile_screen()
            elif choice == '5':
                self.view_user_screen()
            elif choice == '6':
                self.verification_request_screen()
            elif choice == '0':
                success, message = self.user.logout()
                print(f"\n{message}")
                break
    
    def run(self):
        """Запуск приложения"""
        while True:
            self.clear_screen()
            self.print_header()
            
            menu = {
                '1': '🔐 Войти',
                '2': '📝 Зарегистрироваться',
                '3': '📰 Просмотреть ленту (без входа)',
                '0': '❌ Выход'
            }
            
            self.print_menu(menu, "Добро пожаловать!")
            
            choice = input(f"\n{Colors.CYAN}Ваш выбор: {Colors.END}").strip()
            
            if choice == '1':
                self.login_screen()
                if self.user.current_user:
                    self.main_menu()
            elif choice == '2':
                self.register_screen()
            elif choice == '3':
                self.feed_screen()
            elif choice == '0':
                self.clear_screen()
                print(f"\n{Colors.CYAN}👋 Спасибо за использование Netta! До встречи!{Colors.END}\n")
                break


# ═══════════════════════════════════════════════════════════════
# 🚀 ЗАПУСК ПРИЛОЖЕНИЯ
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = NettaApp()
    app.run()
