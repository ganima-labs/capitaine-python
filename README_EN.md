# Capitaine Python 🐍

An interactive learning platform for teaching Python to beginners with FastAPI and Docker.

## 📖 Description

Capitaine Python is a complete educational system that allows beginners to learn Python programming fundamentals in an interactive way. The application combines a robust backend API with a simple frontend interface to create an engaging learning experience.

### ✨ Main Features

- **🎯 Progressive courses**: 13 structured exercises from beginner to autonomous level
- **🌍 Multilingual support**: French, English, Spanish, German
- **🔒 Secure execution**: Code executed in isolated environment (Piston API)
- **📊 Progress tracking**: SQLite database to track learning progress
- **🧪 Complete tests**: 89% coverage with 379 unit tests
- **🐳 Containerization**: Docker Compose for simplified deployment
- **👶 Child mode**: Interface adapted for 8-12 years old with gamification
- **📊 Advanced monitoring**: Docker health checks with Prometheus/Grafana

## 🚀 Installation and Startup

### Prerequisites
- Docker and Docker Compose
- Git (optional, for contribution)

### Quick Installation

1. **Clone the repository**
```bash
git clone https://github.com/vgadreau-pixel/capitaine-python.git
cd capitaine-python
```

2. **Start the environment**
```bash
# Start with Docker Compose
docker-compose up --build -d

# Or for development with auto-reload
docker-compose up --build --force-recreate
```

3. **Access the application**
- Web interface: http://localhost:8080
- API documentation: http://localhost:8080/docs

## 📚 Child Mode (New Feature)

Capitaine Python now has a specialized mode for children aged 8-12:

### 🎮 Child Mode Features
- **🎨 Adapted interface**: Playful and intuitive design
- **🏆 Gamification**: Badges, avatars, visual progression
- **🔒 Enhanced security**: Validation adapted for young learners
- **👨‍👩‍👧‍👦 Parental dashboard**: Monitoring and parental controls
- **📈 Guided progression**: Adapted learning path

### 📊 Complete Documentation
- `docs/planning/CHILD_MODE_IMPLEMENTATION_PLAN.md` - 12-week roadmap
- `docs/security/EXERCISE_PATTERNS_GUIDE.md` - Security/pedagogy patterns
- `docs/design/UI_DESIGN_PROPOSAL.md` - React/TypeScript design
- `docs/monitoring/MONITORING_ADMIN.md` - Docker monitoring

## 🏗️ Architecture

### FastAPI Backend
```
app/
├── backend/
│   ├── main.py              # FastAPI API with 4 endpoints
│   ├── exercises.py          # Educational exercises definitions
│   ├── grader.py            # Secure execution engine
│   ├── db.py                # SQLite progress management
│   ├── security.py          # Code validation and security
│   └── course_manager.py    # JSON course management
├── frontend/
│   ├── index.html           # Single page interface
│   ├── app.js              # Vanilla JavaScript logic
│   └── style.css            # Responsive styles
└── docker-compose.yml
```

### API Endpoints
- `GET /api/exercises` - List all available exercises
- `GET /api/exercises/{eid}` - Details of a specific exercise
- `POST /api/run` - Simple execution (syntax validation)
- `POST /api/grade` - Complete validation with unit tests

#### Course Management Endpoints
- `GET /api/courses` - List all available courses
- `GET /api/courses/{course_id}` - Complete course details
- `GET /api/courses/{course_id}/exercises` - Course exercise list
- `GET /api/courses/{course_id}/exercises/{exercise_id}` - Specific exercise details

## 🧪 Tests

### Running Tests

```bash
# From root directory
docker-compose exec api python -m pytest

# With code coverage
docker-compose exec api python -m pytest --cov=. --cov-report=html

# Specific tests
docker-compose exec api python -m pytest test_main.py -v
```

## 🤝 Contributing

### Contribution Guidelines

1. **Fork the project**
2. **Create a branch** (`git checkout -b feature/new-feature`)
3. **Make changes**
4. **Add tests** if necessary
5. **Submit a Pull Request**

## 📝 License

This project is licensed under MIT.

---

**🐍 Happy Learning with Capitaine Python!**