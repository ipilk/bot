# Discord Music Bot 🎵

بوت ديسكورد لتشغيل المقاطع الصوتية من يوتيوب في قنوات الديسكورد الصوتية.

## المميزات 🌟
- تشغيل مقاطع صوتية من يوتيوب
- دعم الأوامر السريعة (Slash Commands)
- التحكم في التشغيل (إيقاف مؤقت، استئناف، إيقاف)
- عرض المقطع الحالي
- جودة صوت عالية

## الأوامر المتاحة 📝
- `/play [رابط]` - تشغيل مقطع صوتي من يوتيوب
- `/stop` - إيقاف التشغيل والخروج من القناة
- `/pause` - إيقاف التشغيل مؤقتاً
- `/resume` - استئناف التشغيل
- `/nowplaying` - عرض المقطع الحالي

## المتطلبات 📋
- Python 3.8 أو أحدث
- FFmpeg
- توكن بوت ديسكورد

## التثبيت المحلي 🚀
1. قم بتثبيت المتطلبات:
```bash
pip install -r requirements.txt
```

2. قم بإنشاء ملف `.env` وأضف توكن البوت:
```env
DISCORD_TOKEN=your_token_here
```

3. قم بتشغيل البوت:
```bash
python bot.py
```

## النشر على Railway 🚂
1. قم بإنشاء حساب على [Railway](https://railway.app/)
2. اربط مشروعك من GitHub
3. أضف المتغيرات البيئية:
   - `DISCORD_TOKEN`: توكن البوت الخاص بك
4. سيتم نشر البوت تلقائياً

## المساهمة 🤝
نرحب بمساهماتكم! يمكنكم:
1. عمل Fork للمشروع
2. إنشاء فرع جديد (`git checkout -b feature/amazing-feature`)
3. عمل Commit للتغييرات (`git commit -m 'Add amazing feature'`)
4. رفع التغييرات (`git push origin feature/amazing-feature`)
5. فتح Pull Request 