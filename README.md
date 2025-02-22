# Film Öneri Sistemi

Bu proje, MovieLens 20M veri setini kullanarak film önerileri sunan bir sistemdir. Kullanıcıların beğenilerine ve popülerliğe dayalı öneriler sunar. Tkinter ile grafik arayüzü (GUI) geliştirilmiş olup, kullanıcı dostu bir deneyim sağlanmıştır.

## Özellikler

- **Popüler Filmler:** En çok izlenen ve yüksek puan alan filmleri listeler.
- **Tür Bazlı Öneriler:** Kullanıcının seçtiği türe göre en iyi 50 filmi gösterir.
- **Kullanıcı Beğenileri:** Kullanıcıların izlediği ve beğendiği filmleri kaydedip öneri sunar.
- **Kişiselleştirilmiş Öneriler:** Kullanıcıların beğenilerine göre en iyi filmleri önerir.
- **Admin Paneli:** Kullanıcıların verilerini yönetir.

## Kullanılan Teknolojiler

- **Python**: Veri işleme ve GUI geliştirme
- **Tkinter**: Kullanıcı arayüzü
- **Pandas**: Veri analizi
- **MovieLens 20M Dataset**: Film verileri
- **Association Rules & Apriori Algoritması**: Kullanıcı beğenilerine dayalı öneriler

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install pandas tkinter
   ```
2. Projeyi klonlayın:
   ```bash
   git clone https://github.com/kullanici/film-oneri-sistemi.git
   ```
3. Ana Python dosyasını çalıştırın:
   ```bash
   python main.py
   ```
4."*****EK OLARAK ratings.csv dosyası indiriliğ data klasörüne atılmalı dosya büyüklüğünden dolayı yüklenmemiştir*****
## Yapılan Testler

- **Veri Doğrulama:** Film ve puanlama verilerinin uygun formatta olup olmadığı kontrol edildi.
- **Öneri Doğruluğu:** Kullanıcı beğenilerine göre önerilerin mantıklı olup olmadığı test edildi.
- **GUI İşlevselliği:** Tkinter arayüzünün hatasız çalıştığı test edildi.

##

