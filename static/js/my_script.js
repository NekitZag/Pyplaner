const tasksListElement = document.querySelector(`.test-flex`);
const taskElements = tasksListElement.querySelectorAll(`.one`);

// Перебираем все элементы списка и присваиваем нужное значение
for (const task of taskElements) {
  task.draggable = true;
}

tasksListElement.addEventListener(`dragstart`, (evt) => {
  evt.target.classList.add(`selected`);
})

tasksListElement.addEventListener(`dragend`, (evt) => {
  evt.target.classList.remove(`selected`);
});

tasksListElement.addEventListener(`dragover`, (evt) => {
  // Разрешаем сбрасывать элементы в эту область
  evt.preventDefault();

  // Находим перемещаемый элемент
  const activeElement = tasksListElement.querySelector(`.selected`);
  // Находим элемент, над которым в данный момент находится курсор
  const currentElement = evt.target;
  // Проверяем, что событие сработало:
  // 1. не на том элементе, который мы перемещаем,
  // 2. именно на элементе списка
  const isMoveable = activeElement !== currentElement &&
    currentElement.classList.contains(`one`);

  // Если нет, прерываем выполнение функции
  if (!isMoveable) {
    return;
  }

  // Находим элемент, перед которым будем вставлять
  const nextElement = (currentElement === activeElement.nextElementSibling) ?
      currentElement.nextElementSibling :
      currentElement;

  // Вставляем activeElement перед nextElement
  tasksListElement.insertBefore(activeElement, nextElement);
});