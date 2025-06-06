# 🧩 Team Platform / AsyncTeach

**Team Platform** — это микросервисная платформа, разработанная для командной работы над программными продуктами. Проект реализован с нуля с применением современных практик — каждый сервис изолирован и может развиваться независимо.

---

## 📦 Стек технологий

- Python 3.11
- FastAPI
- Django
- Docker + Docker Compose
- VS Code
- GitHub

---

## ⚙️ Архитектура

Проект построен по микросервисному принципу и включает в себя:

```
team-platform/
├── auth_service/              # Аутентификация и авторизация
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── catalog_service/           # Каталог товаров или ресурсов
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                  # Статический фронтенд
│   ├── public/index.html
│   └── Dockerfile
├── docker-compose.yml         # Инфраструктура проекта
└── README.md
```

---

## 🧑‍💻 Разработка

Каждый участник команды работает в своей зоне ответственности:

- **Heisenberg** — разработка `auth_service` (регистрация, авторизация, восстановление пароля), `frontend`
- **Pinkman** — работает над `catalog_service`, `frontend`


## 📁 TODO

- [ ] Реализовать логику `auth_service`
- [ ] Настроить JWT и CORS
- [ ] Подключить базы данных
- [ ] Разделить `.env` файлы для сервисов
- [ ] Добавить документацию к API
- [ ] Написать автотесты

---
