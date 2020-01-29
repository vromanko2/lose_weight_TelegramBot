# lose_weight_telegram_bot

### Завантаження необхідних бібліотек

```
pip install -r requirements.txt
```

### Завантаження моделі для знаходження ключових точок руки 

```
sudo chmod a+x getModels.sh
./getModels.sh

або

sh getModels.sh

## Перевірте, у папці hand/ має бути два файли: pose_deploy.prototxt та pose_iter_102000.caffemodel
```
Також файли знаходяться на [Google Drive](https://drive.google.com/drive/folders/1VuHhAsnWpuiivlAkXQAPvplPFX6eWNHi?usp=sharing). Ви можете завантажити з Drive папку hand та перемістити її до директорії з проектом. 

### Результат роботи моделі

```
python test_hand_detection.py <фото руки>

## Приклад : python test_hand_detection.py hand.jpg
## Результат : hand-test.jpg
```

### Запуск телеграм-бота

```
python bot.py

В вашому телеграм-додатку: 
    
    @lose_weight_with_bot
    
    /start
    
    ## Далі слід слідувати вказівкам бота
```
