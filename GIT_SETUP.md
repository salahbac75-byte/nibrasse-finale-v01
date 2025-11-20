# دليل ربط المشروع بـ Git

## الخطوة 1: تهيئة Git محلياً
```bash
cd d:/TEST/opti_dash/rag-with-antgravity
git init
git add .
git commit -m "feat: Complete RAG system with hybrid search

- Implemented FastAPI backend with upload and query endpoints
- Added Gemini embeddings integration
- Implemented ChromaDB for vector storage
- Added Supabase for metadata storage
- Implemented hybrid search (70% semantic + 30% keyword)
- Added re-ranking with deduplication
- Created modern dark-themed frontend with RTL support
- Added multi-file upload support
- Professional academic-style answer generation"
```

## الخطوة 2: ربط بالمستودع البعيد
```bash
# استبدل YOUR_USERNAME باسم المستخدم الخاص بك
git remote add origin https://github.com/YOUR_USERNAME/rag-arabic-supabase.git

# أو إذا كنت تستخدم SSH:
# git remote add origin git@github.com:YOUR_USERNAME/rag-arabic-supabase.git
```

## الخطوة 3: رفع الكود
```bash
git branch -M main
git push -u origin main
```

## الخطوة 4: التحقق
```bash
git remote -v
```

يجب أن ترى:
```
origin  https://github.com/YOUR_USERNAME/rag-arabic-supabase.git (fetch)
origin  https://github.com/YOUR_USERNAME/rag-arabic-supabase.git (push)
```

---

## 🔐 المصادقة

إذا طُلب منك اسم المستخدم وكلمة المرور:

### الطريقة 1: Personal Access Token (مستحسن)
1. اذهب إلى GitHub Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. اختر الصلاحيات: `repo` (كامل)
4. انسخ الـ token
5. استخدمه بدلاً من كلمة المرور

### الطريقة 2: SSH Key
```bash
# توليد SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# نسخ المفتاح العام
cat ~/.ssh/id_ed25519.pub

# أضفه في GitHub Settings → SSH and GPG keys
```

---

## 📝 أوامر Git المفيدة للمستقبل

```bash
# عرض الحالة
git status

# إضافة تغييرات جديدة
git add .
git commit -m "وصف التغيير"
git push

# سحب آخر التحديثات
git pull

# عرض السجل
git log --oneline

# إنشاء فرع جديد
git checkout -b feature/new-feature

# العودة لفرع main
git checkout main
```

---

## 🏷️ إنشاء Tag للنسخة الحالية

```bash
git tag -a v1.0.0 -m "Initial release: RAG system with hybrid search"
git push origin v1.0.0
```
