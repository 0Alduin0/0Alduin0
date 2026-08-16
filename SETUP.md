# Kurulum ve bakım

Bu depo `0Alduin0/0Alduin0` GitHub profil README’sidir.

## Otomatik güncelleme

`.github/workflows/update-profile.yml` aşağıdaki işlemleri yapar:

1. Unity temalı `assets/hero.gif` kapağını yeniden üretir.
2. `0Alduin0` hesabının gerçek GitHub katkılarını, herkese açık depolarını, takipçilerini ve öne çıkan dillerini çeker.
3. `assets/contribution-city.svg` dosyasını günceller.
4. Yalnızca görseller değiştiğinde `github-actions[bot]` ile commit atar.

Workflow her gün 02:17 UTC’de, elle tetiklendiğinde ve üretim girdileri `main` dalına gönderildiğinde çalışır. Depo ayarlarında **Settings → Actions → General → Workflow permissions → Read and write permissions** seçeneğinin açık olması gerekir.

## Yerelde kapak üretme

```bash
python -m pip install -r requirements.txt
python scripts/generate_hero.py --name "ENES YÜREKLİ" --role "UNITY OYUN GELİŞTİRİCİSİ"
```

Kaynak görsel `assets/base-scene.png`, çıktılar `assets/hero.gif` ve `assets/hero-preview.png` dosyalarıdır. Metin ölçüleri betik tarafından kullanılabilir alana göre otomatik küçültülür.

## Katkı şehrini deneme

Gerçek veri için `GITHUB_TOKEN` ortam değişkeni gerekir:

```bash
python scripts/update_dashboard.py --username "0Alduin0" --display-name "ENES YÜREKLİ"
```

İnternet veya token olmadan yalnızca yerleşimi kontrol etmek için:

```bash
python scripts/update_dashboard.py --username "0Alduin0" --display-name "ENES YÜREKLİ" --offline
```
