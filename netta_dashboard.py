#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════╗
║              🔴 NETTA DASHBOARD - Панель администратора        ║
║                         Версия 1.0                             ║
╚═══════════════════════════════════════════════════════════════╝
"""

import sqlite3
import hashlib
import os
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# 🎨 ЦВЕТА И СТИЛИ
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

BLUE_CHECK = f"{Colors.BLUE}✓{Colors.END}"
RED_CHECK = f"{Colors.RED}✓{Colors.END}"

# ═══════════════════════════════════════════════════════════════
# 🛡️ АДМИН-ПАНЕЛЬ
# ═══════════════════════════════════════════════════════════════

class AdminDashboard:
    def __init__(self, db_name="netta.db"):
        self.db_name = db_name
        self.admin_logged_in = False
        self.admin_user = None
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def print_header(self):
        print(f"""
{Colors.RED}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ██████╗  █████╗ ███████╗██╗  ██╗██████╗  ██████╗  █████╗ ██████╗ ██████╗  ║
║     ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗ ║
║     ██║  ██║███████║███████╗███████║██████╔╝██║   ██║███████║██████╔╝██║  ██║ ║
║     ██║  ██║██╔══██║╚════██║██╔══██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║ ║
║     ██████╔╝██║  ██║███████║██║  ██║██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝ ║
║     ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ║
║                                                               ║
║                 🔴 NETTA ADMIN DASHBOARD                       ║
╚═══════════════════════════════════════════════════════════════╝{Colors.END}
        """)
    
    def print_menu(self, options, title="Меню"):
        print(f"\n{Colors.RED}{'═' * 60}")
        print(f"  🛡️ {title}")
        print(f"{'═' * 60}{Colors.END}")
        
        for key, value in options.items():
            print(f"  {Colors.YELLOW}[{key}]{Colors.END} {value}")
        
        print(f"{Colors.RED}{'═' * 60}{Colors.END}")
    
    def create_first_admin(self):
        """Создание первого администратора"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже администраторы
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print(f"\n{Colors.YELLOW}⚠️ Администраторы не найдены. Создайте первого админа.{Colors.END}\n")
            
            username = input(f"{Colors.CYAN}👤 Имя пользователя: {Colors.END}").strip()
            email = input(f"{Colors.CYAN}📧 Email: {Colors.END}").strip()
            password = input(f"{Colors.CYAN}🔒 Пароль: {Colors.END}").strip()
            display_name = input(f"{Colors.CYAN}📛 Отображаемое имя: {Colors.END}").strip() or username
            
            password_hash = self.hash_password(password)
            
            try:
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, display_name, 
                                      is_admin, verification_status)
                    VALUES (?, ?, ?, ?, 1, 1)
                ''', (username, email, password_hash, display_name))
                
                conn.commit()
                print(f"\n{Colors.GREEN}✅ Администратор {username} успешно создан!{Colors.END}")
            except sqlite3.IntegrityError as e:
                print(f"\n{Colors.RED}❌ Ошибка: {e}{Colors.END}")
        
        conn.close()
    
    def admin_login(self):
        """Вход администратора"""
        self.clear_screen()
        self.print_header()
        
        print(f"\n{Colors.RED}{'═' * 50}")
        print("  🔐 ВХОД В АДМИН-ПАНЕЛЬ")
        print(f"{'═' * 50}{Colors.END}\n")
        
        username = input(f"{Colors.CYAN}👤 Логин администратора: {Colors.END}").strip()
        password = input(f"{Colors.CYAN}🔒 Пароль: {Colors.END}").strip()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password_hash = ? AND is_admin = 1
        ''', (username, password_hash))
        
        admin = cursor.fetchone()
        conn.close()
        
        if admin:
            self.admin_logged_in = True
            self.admin_user = {
                'id': admin[0],
                'username': admin[1],
                'display_name': admin[4]
            }
            print(f"\n{Colors.GREEN}✅ Добро пожаловать, {admin[4]}!{Colors.END}")
            input("\nНажмите Enter...")
            return True
        else:
            print(f"\n{Colors.RED}❌ Неверные данные или недостаточно прав!{Colors.END}")
            input("\nНажмите Enter...")
            return False
    
    def view_all_users(self):
        """Просмотр всех пользователей"""
        self.clear_screen()
        print(f"\n{Colors.GREEN}{'═' * 80}")
        print("  👥 СПИСОК ПОЛЬЗОВАТЕЛЕЙ")
        print(f"{'═' * 80}{Colors.END}\n")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, display_name, email, verification_status, 
                   is_admin, created_at, followers_count
            FROM users ORDER BY id DESC
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        print(f"{Colors.CYAN}{'ID':<5} {'Username':<15} {'Имя':<20} {'Статус':<20} {'Подписчики':<10}{Colors.END}")
        print("─" * 80)
        
        for user in users:
            status = ""
            if user[5] == 1:
                status = f"{Colors.RED}🔴 Админ{Colors.END}"
            elif user[4] == 1:
                status = f"{Colors.BLUE}🔵 Верифицирован{Colors.END}"
            else:
                status = "⚪ Обычный"
            
            print(f"{user[0]:<5} {user[1]:<15} {user[2]:<20} {status:<30} {user[7]:<10}")
        
        print("─" * 80)
        print(f"Всего пользователей: {len(users)}")
        
        input("\nНажмите Enter для продолжения...")
    
    def view_verification_requests(self):
        """Просмотр заявок на верификацию"""
        self.clear_screen()
        print(f"\n{Colors.BLUE}{'═' * 80}")
        print(f"  {BLUE_CHECK} ЗАЯВКИ НА ВЕРИФИКАЦИЮ")
        print(f"{'═' * 80}{Colors.END}\n")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT vr.id, u.username, u.display_name, vr.reason, vr.status, vr.created_at
            FROM verification_requests vr
            JOIN users u ON vr.user_id = u.id
            WHERE vr.status = 'pending'
            ORDER BY vr.created_at DESC
        ''')
        
        requests = cursor.fetchall()
        conn.close()
        
        if not requests:
            print(f"{Colors.YELLOW}Нет активных заявок на верификацию{Colors.END}")
        else:
            for req in requests:
                print(f"""
{Colors.WHITE}┌────────────────────────────────────────────────────────────────┐
│ {Colors.CYAN}ID заявки: {req[0]}{Colors.WHITE}
│ {Colors.CYAN}Пользователь:{Colors.END} @{req[1]} ({req[2]})
│ {Colors.CYAN}Причина:{Colors.END} {req[3]}
│ {Colors.CYAN}Дата подачи:{Colors.END} {req[5]}
│ {Colors.CYAN}Статус:{Colors.END} {Colors.YELLOW}{req[4]}{Colors.END}
{Colors.WHITE}└────────────────────────────────────────────────────────────────┘{Colors.END}
                """)
        
        input("\nНажмите Enter для продолжения...")
    
    def approve_verification(self):
        """Одобрить заявку на верификацию"""
        self.clear_screen()
        print(f"\n{Colors.GREEN}{'═' * 50}")
        print(f"  ✅ ОДОБРИТЬ ВЕРИФИКАЦИЮ")
        print(f"{'═' * 50}{Colors.END}\n")
        
        request_id = input(f"{Colors.CYAN}ID заявки: {Colors.END}").strip()
        
        try:
            request_id = int(request_id)
        except:
            print(f"\n{Colors.RED}❌ Неверный ID!{Colors.END}")
            input("\nНажмите Enter...")
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Получаем user_id из заявки
        cursor.execute('SELECT user_id FROM verification_requests WHERE id = ?', (request_id,))
        result = cursor.fetchone()
        
        if not result:
            print(f"\n{Colors.RED}❌ Заявка не найдена!{Colors.END}")
            conn.close()
            input("\nНажмите Enter...")
            return
        
        user_id = result[0]
        
        # Обновляем статус заявки
        cursor.execute('''
            UPDATE verification_requests SET status = 'approved' WHERE id = ?
        ''', (request_id,))
        
        # Обновляем верификацию пользователя
        cursor.execute('''
            UPDATE users SET verification_status = 1 WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        print(f"\n{Colors.GREEN}✅ Верификация одобрена! Пользователь получил синюю галочку {BLUE_CHECK}{Colors.END}")
        input("\nНажмите Enter...")
    
    def reject_verification(self):
        """Отклонить заявку на верификацию"""
        self.clear_screen()
        print(f"\n{Colors.RED}{'═' * 50}")
        print("  ❌ ОТКЛОНИТЬ ВЕРИФИКАЦИЮ")
        print(f"{'═' * 50}{Colors.END}\n")
        
        request_id = input(f"{Colors.CYAN}ID заявки: {Colors.END}").strip()
        
        try:
            request_id = int(request_id)
        except:
            print(f"\n{Colors.RED}❌ Неверный ID!{Colors.END}")
            input("\nНажмите Enter...")
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE verification_requests SET status = 'rejected' WHERE id = ?
        ''', (request_id,))
        
        conn.commit()
        conn.close()
        
        print(f"\n{Colors.YELLOW}❌ Заявка отклонена!{Colors.END}")
        input("\nНажмите Enter...")
    
    def grant_admin(self):
        """Выдать права администратора"""
        self.clear_screen()
        print(f"\n{Colors.RED}{'═' * 50}")
        print(f"  {RED_CHECK} НАЗНАЧИТЬ АДМИНИСТРАТОРА")
        print(f"{'═' * 50}{Colors.END}\n")
        
        username = input(f"{Colors.CYAN}@username пользователя: {Colors.END}").strip().replace('@', '')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, display_name FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"\n{Colors.RED}❌ Пользователь не найден!{Colors.END}")
            conn.close()
            input("\nНажмите Enter...")
            return
        
        confirm = input(f"\n{Colors.YELLOW}Вы уверены, что хотите сделать {user[1]} администратором? (да/нет): {Colors.END}")
        
        if confirm.lower() == 'да':
            cursor.execute('''
                UPDATE users SET is_admin = 1, verification_status = 1 WHERE id = ?
            ''', (user[0],))
            conn.commit()
            print(f"\n{Colors.GREEN}✅ {user[1]} теперь администратор! {RED_CHECK}{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}Операция отменена{Colors.END}")
        
        conn.close()
        input("\nНажмите Enter...")
    
    def revoke_verification(self):
        """Отозвать верификацию"""
        self.clear_screen()
        print(f"\n{Colors.YELLOW}{'═' * 50}")
        print("  ⚠️ ОТОЗВАТЬ ВЕРИФИКАЦИЮ")
        print(f"{'═' * 50}{Colors.END}\n")
        
        username = input(f"{Colors.CYAN}@username пользователя: {Colors.END}").strip().replace('@', '')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, display_name FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"\n{Colors.RED}❌ Пользователь не найден!{Colors.END}")
            conn.close()
            input("\nНажмите Enter...")
            return
        
        cursor.execute('''
            UPDATE users SET verification_status = 0 WHERE id = ?
        ''', (user[0],))
        
        conn.commit()
        conn.close()
        
        print(f"\n{Colors.YELLOW}⚠️ Верификация пользователя {user[1]} отозвана!{Colors.END}")
        input("\nНажмите Enter...")
    
    def delete_user(self):
        """Удалить пользователя"""
        self.clear_screen()
        print(f"\n{Colors.RED}{'═' * 50}")
        print("  🗑️ УДАЛИТЬ ПОЛЬЗОВАТЕЛЯ")
        print(f"{'═' * 50}{Colors.END}\n")
        
        username = input(f"{Colors.CYAN}@username пользователя: {Colors.END}").strip().replace('@', '')
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, display_name, is_admin FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"\n{Colors.RED}❌ Пользователь не найден!{Colors.END}")
            conn.close()
            input("\nНажмите Enter...")
            return
        
        if user[2] == 1:
            print(f"\n{Colors.RED}❌ Нельзя удалить администратора!{Colors.END}")
            conn.close()
            input("\nНажмите Enter...")
            return
        
        confirm = input(f"\n{Colors.RED}⚠️ ВНИМАНИЕ! Удалить пользователя {user[1]} и все его данные? (да/нет): {Colors.END}")
        
        if confirm.lower() == 'да':
            # Удаляем посты
            cursor.execute('DELETE FROM neets WHERE user_id = ?', (user[0],))
            # Удаляем лайки
            cursor.execute('DELETE FROM likes WHERE user_id = ?', (user[0],))
            # Удаляем подписки
            cursor.execute('DELETE FROM follows WHERE follower_id = ? OR following_id = ?', (user[0], user[0]))
            # Удаляем заявки на верификацию
            cursor.execute('DELETE FROM verification_requests WHERE user_id = ?', (user[0],))
            # Удаляем пользователя
            cursor.execute('DELETE FROM users WHERE id = ?', (user[0],))
            
            conn.commit()
            print(f"\n{Colors.GREEN}✅ Пользователь {user[1]} удален!{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}Операция отменена{Colors.END}")
        
        conn.close()
        input("\nНажмите Enter...")
    
    def delete_neet(self):
        """Удалить пост"""
        self.clear_screen()
        print(f"\n{Colors.RED}{'═' * 50}")
        print("  🗑️ УДАЛИТЬ NEET")
        print(f"{'═' * 50}{Colors.END}\n")
        
        neet_id = input(f"{Colors.CYAN}ID поста: {Colors.END}").strip()
        
        try:
            neet_id = int(neet_id)
        except:
            print(f"\n{Colors.RED}❌ Неверный ID!{Colors.END}")
            input("\nНажмите Enter...")
            return
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT content FROM neets WHERE id = ?', (neet_id,))
        neet = cursor.fetchone()
        
        if not neet:
            print(f"\n{Colors.RED}❌ Пост не найден!{Colors.END}")
            conn.close()
            input("\nНажмите Enter...")
            return
        
        print(f"\n{Colors.YELLOW}Содержание поста: {neet[0][:100]}...{Colors.END}")
        confirm = input(f"\n{Colors.RED}Удалить этот пост? (да/нет): {Colors.END}")
        
        if confirm.lower() == 'да':
            cursor.execute('DELETE FROM likes WHERE neet_id = ?', (neet_id,))
            cursor.execute('DELETE FROM neets WHERE id = ?', (neet_id,))
            conn.commit()
            print(f"\n{Colors.GREEN}✅ Пост удален!{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}Операция отменена{Colors.END}")
        
        conn.close()
        input("\nНажмите Enter...")
    
    def view_statistics(self):
        """Просмотр статистики"""
        self.clear_screen()
        print(f"\n{Colors.GREEN}{'═' * 50}")
        print("  📊 СТАТИСТИКА NETTA")
        print(f"{'═' * 50}{Colors.END}\n")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        users_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_admin = 1')
        admins_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE verification_status = 1 AND is_admin = 0')
        verified_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM neets')
        neets_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM likes')
        likes_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM verification_requests WHERE status = 'pending'")
        pending_requests = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"""
{Colors.CYAN}┌────────────────────────────────────────────────────┐
│                   📊 СТАТИСТИКА                    │
├────────────────────────────────────────────────────┤
│                                                    │
│   👥 Всего пользователей:        {users_count:<10}         │
│   {RED_CHECK} Администраторов:              {admins_count:<10}         │
│   {BLUE_CHECK} Верифицированных:             {verified_count:<10}         │
│                                                    │
│   📝 Всего Neets:                {neets_count:<10}         │
│   ❤️ Всего лайков:               {likes_count:<10}         │
│                                                    │
│   📋 Заявок на рассмотрении:     {pending_requests:<10}         │
│                                                    │
└────────────────────────────────────────────────────┘{Colors.END}
        """)
        
        input("\nНажмите Enter для продолжения...")
    
    def main_menu(self):
        """Главное меню админ-панели"""
        while self.admin_logged_in:
            self.clear_screen()
            self.print_header()
            
            print(f"\n{Colors.RED}Администратор: {Colors.BOLD}{self.admin_user['display_name']}{Colors.END} {RED_CHECK}")
            
            menu = {
                '1': '👥 Все пользователи',
                '2': '📋 Заявки на верификацию',
                '3': f'✅ Одобрить верификацию {BLUE_CHECK}',
                '4': '❌ Отклонить верификацию',
                '5': f'🔴 Назначить администратора {RED_CHECK}',
                '6': '⚠️ Отозвать верификацию',
                '7': '🗑️ Удалить пользователя',
                '8': '🗑️ Удалить Neet',
                '9': '📊 Статистика',
                '0': '🚪 Выход'
            }
            
            self.print_menu(menu, "Админ-панель")
            
            choice = input(f"\n{Colors.CYAN}Ваш выбор: {Colors.END}").strip()
            
            if choice == '1':
                self.view_all_users()
            elif choice == '2':
                self.view_verification_requests()
            elif choice == '3':
                self.approve_verification()
            elif choice == '4':
                self.reject_verification()
            elif choice == '5':
                self.grant_admin()
            elif choice == '6':
                self.revoke_verification()
            elif choice == '7':
                self.delete_user()
            elif choice == '8':
                self.delete_neet()
            elif choice == '9':
                self.view_statistics()
            elif choice == '0':
                self.admin_logged_in = False
                print(f"\n{Colors.YELLOW}👋 До свидания!{Colors.END}")
                break
    
    def run(self):
        """Запуск админ-панели"""
        self.clear_screen()
        self.print_header()
        
        # Проверяем/создаем первого админа
        self.create_first_admin()
        
        while True:
            if self.admin_login():
                self.main_menu()
                break
            else:
                retry = input(f"\n{Colors.CYAN}Попробовать снова? (да/нет): {Colors.END}")
                if retry.lower() != 'да':
                    break


# ═══════════════════════════════════════════════════════════════
# 🚀 ЗАПУСК АДМИН-ПАНЕЛИ
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    dashboard = AdminDashboard()
    dashboard.run()
