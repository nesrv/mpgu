// Переключаемся на БД 'library' (создастся автоматически при первой записи)
use library;

// Очистка (опционально — закомментируй, если не хочешь удалять старые данные)
db.authors.deleteMany({});
db.books.deleteMany({});
db.reviews.deleteMany({});

// Вставляем авторов
const authors = db.authors.insertMany([
  { name: "Лев Толстой", birthYear: 1828, country: "Россия" },
  { name: "Фёдор Достоевский", birthYear: 1821, country: "Россия" },
  { name: "Джордж Оруэлл", birthYear: 1903, country: "Великобритания" },
  { name: "Габриэль Гарсиа Маркес", birthYear: 1927, country: "Колумбия" }
]);

// Получаем ID авторов для связи
const authorIds = Object.values(authors.insertedIds);
const [tolstoy, dostoevsky, orwell, garcia] = authorIds;

// Вставляем книги
db.books.insertMany([
  {
    title: "Война и мир",
    authorId: tolstoy,
    pages: 1225,
    publishedYear: 1869,
    genre: "роман"
  },
  {
    title: "Анна Каренина",
    authorId: tolstoy,
    pages: 864,
    publishedYear: 1877,
    genre: "роман"
  },
  {
    title: "Преступление и наказание",
    authorId: dostoevsky,
    pages: 671,
    publishedYear: 1866,
    genre: "роман"
  },
  {
    title: "1984",
    authorId: orwell,
    pages: 328,
    publishedYear: 1949,
    genre: "антиутопия"
  },
  {
    title: "Сто лет одиночества",
    authorId: garcia,
    pages: 417,
    publishedYear: 1967,
    genre: "магический реализм"
  }
]);

// Получаем ID книг для отзывов
const books = db.books.find().toArray();
const bookIds = {};
books.forEach(book => {
  if (book.title === "Война и мир") bookIds.war = book._id;
  if (book.title === "1984") bookIds.orwell = book._id;
  if (book.title === "Преступление и наказание") bookIds.crime = book._id;
});

// Вставляем отзывы
db.reviews.insertMany([
  { bookId: bookIds.war, rating: 5, comment: "Величайший роман всех времён!", reviewerName: "Анна" },
  { bookId: bookIds.war, rating: 4, comment: "Долго читать, но того стоит.", reviewerName: "Иван" },
  { bookId: bookIds.orwell, rating: 5, comment: "Актуально как никогда.", reviewerName: "Мария" },
  { bookId: bookIds.orwell, rating: 3, comment: "Мрачновато, но интересно.", reviewerName: "Сергей" },
  { bookId: bookIds.crime, rating: 5, comment: "Потрясающая глубина персонажей.", reviewerName: "Елена" }
]);

