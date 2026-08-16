# Kurulum ve bakım

Bu depo `0Alduin0/0Alduin0` GitHub profil README’sidir.

## Otomatik güncelleme

`.github/workflows/update-profile.yml` aşağıdaki işlemleri yapar:

1. Unity temalı `assets/hero.gif` kapağını yeniden üretir.
2. Betikleri ve üretilen görselleri doğrular.
3. Yalnızca kapak değiştiğinde `github-actions[bot]` ile commit atar.

Workflow elle tetiklendiğinde veya kapak üretim girdileri `main` dalına gönderildiğinde çalışır. Depo ayarlarında **Settings → Actions → General → Workflow permissions → Read and write permissions** seçeneğinin açık olması gerekir.

## Yerelde kapak üretme

```bash
python -m pip install -r requirements.txt
python scripts/generate_hero.py --name "ENES YÜREKLİ" --role "UNITY OYUN GELİŞTİRİCİSİ"
```

Kaynak görsel `assets/base-scene.png`, çıktılar `assets/hero.gif` ve `assets/hero-preview.png` dosyalarıdır. Metin ölçüleri betik tarafından kullanılabilir alana göre otomatik küçültülür. README içindeki kapak bağlantısı tıklandığında herkese açık depolar açılır.

## Katkı şehrini deneme

Gerçek veri için `GITHUB_TOKEN` ortam değişkeni gerekir:

```bash
python scripts/update_dashboard.py --username "0Alduin0" --display-name "ENES YÜREKLİ"
```

İnternet veya token olmadan yalnızca yerleşimi kontrol etmek için:

```bash
python scripts/update_dashboard.py --username "0Alduin0" --display-name "ENES YÜREKLİ" --offline
```
