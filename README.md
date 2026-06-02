# Warehouse Robotics Simulation

Bu proje, bir depo içinde çalışan otonom mobil robotların görev alma, rota izleme, bekleme ve teslim davranışlarını zaman adımlı olarak simüle eder. Amaç, farklı robot sayılarında sistemin nasıl değiştiğini ölçmek ve sonuçları anlaşılır tablolarla ve grafiklerle yorumlamaktır.

## Projenin Amacı

Çalışmanın ana hedefi, sabit bir depo düzeninde ve aynı görev listesiyle robot sayısı değiştiğinde performansın nasıl etkilendiğini incelemektir. Bu nedenle proje yalnızca çalışan bir Python uygulaması değil; modelleme, simülasyon ve analiz adımlarını birlikte ele alan küçük bir deney ortamı olarak tasarlanmıştır.

## Modelleme Yaklaşımı

Depo iki boyutlu bir grid olarak temsil edilir. Grid üzerindeki her hücre ya geçilebilir bir yol, ya raf/engel, ya da robotların kullandığı özel bir nokta olabilir.

| Sembol | Anlam |
|---|---|
| `0` | Geçilebilir yol |
| `1` | Raf veya engel |
| `S` | Robot başlangıç noktası |
| `P` | Ürün alma noktası |
| `D` | Teslim noktası |

Her robot kendi konumunu, hedefini, durumunu, atanmış görevini, rotasını, kat ettiği toplam mesafeyi, aktif çalışma süresini ve bekleme süresini tutar. Görev modeli ise ürün alma noktası, teslim noktası, oluşturulma zamanı, atanan robot ve tamamlanma zamanı gibi alanlardan oluşur.

## Simülasyon Akışı

Simülasyon zaman adımlarıyla ilerler. Her adımda bekleyen görevler kontrol edilir, boşta olan robotlara görev atanır, BFS ile rota hesaplanır ve robotlar rotalarındaki bir sonraki hücreye ilerler. Temel trafik kontrolü sayesinde iki robot aynı anda aynı hücreye giremez. Hedef hücre uygun değilse robot o adımda bekler ve bekleme süresi metriğe eklenir.

## Ana Senaryo

`main.py` çalıştırıldığında aşağıdaki ana senaryo otomatik olarak yürütülür:

- Depo boyutu: 20x20
- Görev sayısı: 100
- Robot sayıları: 2, 4, 6, 8
- Robot hızı: 1 hücre / zaman adımı
- Rota algoritması: BFS
- Bitiş koşulu: Tüm görevlerin tamamlanması

## Kullanılan Metrikler

- Toplam tamamlanma süresi
- Ortalama görev tamamlama süresi
- Throughput
- Robot kullanım oranı
- Ortalama bekleme süresi
- Toplam kat edilen mesafe
- Bloklanma / bekleme sayısı
- Zaman içindeki bekleyen görev sayısı

## Çalıştırma

Python 3.10 veya üzeri bir ortamda bağımlılıkları kurup ana dosyayı çalıştırmak yeterlidir.

```bash
pip install -r requirements.txt
python main.py
```

Testleri çalıştırmak için:

```bash
python -m unittest
```

## Üretilen Çıktılar

Simülasyon tamamlandığında özet sonuç tablosu ve zaman serisi kayıtları CSV olarak kaydedilir.

- `outputs/tables/results.csv`
- `outputs/tables/replications_raw.csv`
- `outputs/tables/replication_summary.csv`
- `outputs/tables/time_series_robot_2.csv`
- `outputs/tables/time_series_robot_4.csv`
- `outputs/tables/time_series_robot_6.csv`
- `outputs/tables/time_series_robot_8.csv`

Ayrıca aşağıdaki grafikler PNG formatında üretilir:

- `outputs/figures/total_completion_time_by_robot_count.png`
- `outputs/figures/throughput_by_robot_count.png`
- `outputs/figures/average_waiting_time_by_robot_count.png`
- `outputs/figures/waiting_tasks_over_time.png`
- `outputs/figures/replication_total_completion_time_ci.png`
- `outputs/figures/replication_throughput_ci.png`

## Sonuçları Yorumlama

Robot sayısı arttıkça toplam tamamlanma süresinin azalması beklenir ancak depo trafiği sıkışmaya başladığında bu iyileşme sınırlanabilir. Throughput değerinin yükselmesi, sistemin birim zamanda daha fazla görev tamamladığını gösterir. Ortalama bekleme süresi ve bloklanma sayısı ise robot sayısı arttığında depo içi trafiğin ne kadar zorlandığını anlamak için kullanılır.
