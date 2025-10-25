### 🏦 На чём работают банки с COBOL?

В старых и крупных банковских системах (а таких очень много — особенно в СНГ, Европе, США, Латинской Америке), **ядро** банков (Core Banking Systems) до сих пор написано на **COBOL**, и это не шутка.

Но вот внешние интерфейсы — то, как вы с этим COBOL'ом общаетесь из мира Python, Node, Java и пр. — могут быть разные.

---

### 📡 Какие API используют COBOL-системы в банках?

| Тип API                    | Где и как используется                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------- |
| **SOAP (WSDL)**            | 80% интеграций с внешним миром. Часто используется в Java/.NET шлюзах, оборачивающих COBOL. |
| **MQ (IBM MQ / RabbitMQ)** | Асинхронный обмен сообщениями между front-end и мейнфреймом. Классика.                      |
| **ISO 8583 (TCP)**         | Банковские терминалы, POS'ы, карточные транзакции (очень «низкоуровнево»).                  |
| **REST API**               | Используется как "фасад" — REST → Middleware → SOAP или MQ → COBOL.                         |
| **gRPC / Kafka**           | Редко, но появляются в новых системах. Используются на уровне интеграции.                   |
| **FTP / SFTP файлы**       | Не шутка. Ежедневные batch-передачи из COBOL в XML/CSV и обратно.                           |
| **Direct CICS calls**      | На мейнфреймах через IBM CICS Transaction Server (для Java/COBOL/Assembler).                |

---

### 💡 Как выглядит архитектура?

```
[Mobile App / Web] → REST API → Middleware → SOAP или MQ → COBOL (Mainframe)
```

---

### 📌 Перевод на «язык программистов»:

* **"COBOL сам в API не ходит — к нему ходят."**
* **"Если видишь SOAP с названием operation=DoAccountTransfer — почти точно внутри COBOL."**
* **"Бэк офиса нет, есть мейнфрейм."**
* **"MQ-шечку брось — и жди, пока мейнфрейм отдумается."**
* **"Там ещё FTP с dump-логами крутится по ночам."**

---

### 🧪 Пример реального сценария:

```plaintext
Frontend: JavaScript (React)  
Backend: Java (Spring Boot REST API)  
→ вызывает SOAP  
→ который кладёт сообщение в IBM MQ  
→ его подхватывает CICS / COBOL  
→ обрабатывает транзакцию  
→ кладёт ответ в другую очередь  
→ REST API ждёт или polling'ом проверяет  
→ возвращает клиенту JSON
```

Вот пример **реалистичного SOAP-запроса**, который может использоваться в банковских системах для, скажем, перевода средств между счетами (`AccountTransfer`). Такие запросы характерны для интеграции с **COBOL или core banking системами**.

---

## 🧾 Пример SOAP-запроса — `AccountTransfer`

```xml
POST /BankService HTTP/1.1
Host: bank.example.com
Content-Type: text/xml; charset=utf-8
SOAPAction: "AccountTransfer"

<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:bank="http://example.com/bank">
   <soapenv:Header>
      <bank:Authentication>
         <bank:Username>api_user</bank:Username>
         <bank:Password>secure123</bank:Password>
      </bank:Authentication>
   </soapenv:Header>
   <soapenv:Body>
      <bank:AccountTransferRequest>
         <bank:FromAccount>1234567890</bank:FromAccount>
         <bank:ToAccount>9876543210</bank:ToAccount>
         <bank:Amount>1000.00</bank:Amount>
         <bank:Currency>USD</bank:Currency>
         <bank:Reference>Invoice#2025-07</bank:Reference>
         <bank:TransactionDate>2025-07-25</bank:TransactionDate>
      </bank:AccountTransferRequest>
   </soapenv:Body>
</soapenv:Envelope>
```

---

## 📤 Пример SOAP-ответа:

```xml
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:bank="http://example.com/bank">
   <soapenv:Body>
      <bank:AccountTransferResponse>
         <bank:Status>SUCCESS</bank:Status>
         <bank:TransactionId>TXN123456789</bank:TransactionId>
         <bank:BalanceAfter>4990.00</bank:BalanceAfter>
      </bank:AccountTransferResponse>
   </soapenv:Body>
</soapenv:Envelope>
```

---

### 💬 На сленге:

> **"XML-овая простыня с `soapenv:Envelope`, в которую мы молитвенно кладём `FromAccount`, надеясь, что COBOL-ядро примет жертву и вернёт `SUCCESS`."**

---





