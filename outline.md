# Project Pegasus

**Scopo dell'agente**: esplorare un ambiente alla ricerca delle carote, da lanciare al pony.

**Linguaggi**: Python, Prolog

---

<details>  
<summary><h3>Ambiente</h3></summary>
  Così come il progetto (vedere dopo), l'ambiente può essere sviluppato incrementalmente (ovvero: si aggiungono caratteristiche, alzando il livello di complessità, gradualmente)

  - BASE: semplice stanza quadrata con le carote e il cavallo
  - Labirinto: più stanze collegate da corridoi, generate pseudorandomicamente (ciascuna è un'istanza da risolvere del punto sopra, o qualcosa di simile a handson2)
  - Labirinto buio: osservabilità parziale + possibilità di aggiungere oggetti che fanno luce
  - Cavallo ostile
  - Esercitare l'abilità di cavalcare

</details>

<details>
  <summary><h3>Tasks dell'agente</h3></summary>
  Anche qui, l'idea è quella di *sviluppo incrementale*: si va avanti per passi, insieme, e si aggiungono features quando possibile.
  
  1. [ ] Stanza vuota + cavallo (carote in inventario)
  2. [ ] Stanza vuota + cavallo + carote sparse per la mappa
  3. [ ] Stanza vuota + cavallo + carote + nemici
  4. [ ] Labirinto + cavallo + carote sparse per il labirinto (ovvero nelle stanze)
  5. [ ] Labirinto + cavallo + carote sparse per il labirinto (ovvero nelle stanze) + nemici
     
**Sviluppo incrementale (bonus)**: buio (ad es. dopo i punti  2 e 4), cavallo ostile.
  
</details>

<details>
  <summary><h3>To do</h3></summary>
  
  **Immediate tasks**: 
  - [ ] Verificare che lanciando una razione di trippa a un cavallo ostile, questo diventa pacifico

  **Incontro 23/11**:
  - [x] Nome del team
  - [x] Nome del progetto
  - [x] Creare repository GitHub
  - [x] Iscrivere il gruppo tramite form
  - [ ] Unit test
  - [ ] Creare Notebook con ambiente base per demo 12-15 dicembre
  
</details>

**Known Issues**: 
 - *Non* mangiare/lanciare/posare le mele. Per qualche motivo i programmi danno errore (non riscontrato nella handson2)
 - Due oggetti sulla stessa casella non riescono a stare, in MiniHack. Credo sia un limite di MiniHack che non c'è in NetHack (*Andrea*)

