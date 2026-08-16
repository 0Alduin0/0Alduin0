# Kurulum

Bu paket doğrudan GitHub profil README deposine kopyalanmak üzere hazırlandı.

1. GitHub kullanıcı adınla **birebir aynı isimde** herkese açık bir depo oluştur.
2. Paketteki tüm dosyaları deponun kök dizinine kopyala.
3. `README.md` içindeki proje adlarını, açıklamaları ve bağlantıları istediğin gibi düzenle.
4. GitHub'da **Settings → Actions → General → Workflow permissions** bölümüne gir.
5. **Read and write permissions** seçeneğini etkinleştir.
6. Actions sekmesinden **Update profile dashboard** workflow'unu bir kez elle çalıştır.

Workflow depo sahibinin kullanıcı adını otomatik kullanır; ayrıca kullanıcı adı yazman gerekmez. Başarılı ilk çalıştırmadan sonra `assets/contribution-city.svg` gerçek GitHub verilerinle güncellenir ve her gün yeniden oluşturulur.

## Ana animasyonu değiştirme

Başlık veya rol metnini yeniden render etmek için:

```bash
python -m pip install -r requirements.txt
python scripts/generate_hero.py --name "ENES YÜREKLİ" --role "GAME & BACKEND DEVELOPER"
```

Animasyonun kaynak görseli `assets/base-scene.png`, çıktısı `assets/hero.gif` dosyasıdır. Komut ayrıca sabit önizleme olarak `assets/hero-preview.png` üretir.

## Katkı şehrini yerelde deneme

İnternet veya token olmadan örnek veriyle:

```bash
python scripts/update_dashboard.py --username "github-kullanici-adin" --display-name "ENES YÜREKLİ" --offline
```

Gerçek veriyle çalıştırmak için `GITHUB_TOKEN` ortam değişkeni gerekir. GitHub Actions bunu otomatik sağlar.

