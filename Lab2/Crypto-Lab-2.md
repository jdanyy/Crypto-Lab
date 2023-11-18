# Folyamtitkositok
- [[Crypto Lab 2 rajz]]
- [[SzantoSzollosiKriptoJegyzet.pdf]]
---
Implementáljuk Python programozási nyelvben a következő feladatot:

1. Hozzunk létre egy általános, bájtsorozatot kódoló/dekódoló folyamtitkosítót. A kulcsgeneráló algoritmust és a megfelelő kulcsot paraméterként kapja a folyamtitkosító. **(3p)**
2. Implementáljuk a Solitaire algoritmust ([https://www.schneier.com/academic/solitaire/ (Links to an external site.)Links to an external site.](https://www.schneier.com/academic/solitaire/)) és még egy szabadon választott álvéletlen (szám)sorozat generáló algoritmust (pl. Blum-Blum-Shub) és teszteljük az 1. pontnál implementált folyamtitkosítóval. **(3p)**
3. Implementáljunk két kliens folyamatot, akik hálózaton kommunikálnak egymással (socket, peer-to-peer) titkosított módon. A kommunikáció kétirányú és bármelyik kliens kezdeményezheti. A titkosításhoz az 1. és 2. pontoknál implementált folyamtitkosítót használják. Egy konfigurációs állományban (ami közös) meg van adva a folyamtitkosító algoritmusa (Solitaire vagy a másik, szabadon választott) és a megfelelő kulcs. **(4p)**

## Jegyzet
## Altalanos folyamtitkosito
Stream -> Zajt outputol, random tulajdonkeppen.
1. alpont: XOR-ozzuk.
Ne egy pszeudo random generatort hasznalj (?)
Letrehozni egy altalanos class-t, amelynek van egy config file-ja, ez a class futtat.
- Ez kaphat egy osztalyt, amely leirja, hogy hogyan enkriptal es, ad byteokat.

!! A konfiguracios file tartalmazza: Az algoritmust es a seedet:
~~~json
{
	"algorithm": ...,
	"seed": ...,
}
~~~

A Solitaire az egyik ilyen algoritmus.

```ad-warning
title: Kell legyen ket folyamat, amely socketeken keresztul kommunikal. Ket python file


```

### Solitaire
Az algoritmus seed-je a paklinak az eredeti allapota. 54 kartya, 54! lehetoseg.
A ket `joker` mind 53.
A ket joket harom reszre osztja a paklikat: elso joker elotti, kozott es utanna.

Eloszor megkeressuk a fehet jokert es egyel lentebb szurjuk. (Vagyis hatrabb megy), itt korkorosen kell menjen. A fekete joker eseten $2$ kartyat szok ki.

```ad-info
title: Egy lepes

- Eloszor lep a lassabb joker, aztan a gyorsabb.
```

Kiiras -> 0...51 szamokat kapunk.
Legyen:
- 0..25 <-> a...z
- 26...51 <-> A...Z

Tehat kapunk egy szoveget es ezeket az ertekeket modulosan hozzaadajuk:
alma -> $\hat{0}, \hat{11}, \hat{12}, \hat{0}$ ezt pedig osszeadjuk a Solitarebol kapott ertekeket moduloval. Ez az enkriptalt szoveg.

Most ezt alkalmazni kell byteokra.
Ezert generalunk negy ilyen szamot, modulozzuk 4-el, igy kapunk 4x2 bitet, ez lesz a vegso byte.