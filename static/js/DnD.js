//
////Инициализация родительских классов элементов пилотов и инструкторов
//InstructorsListElement = document.querySelector('.pilots_tab');
//PilotsListElement = document.querySelector('.pilots');
//
////Инициализация списка всех элементов пилотов и инструкторов
//const instructorElements = InstructorsListElement.querySelectorAll('.people');
//const pilotsElements= PilotsListElement.querySelectorAll('.people');
//
//// Перебираем все элементы списка и открываем им свойства перемещения
//for (const inst of instructorElements) {
//  inst.draggable = true;
//}
//
//for (const pilo of pilotsElements) {
//  pilo.draggable = true;
//}
//
////Начало действия перемещения инструкторов
//InstructorsListElement.addEventListener(`dragstart`, (evt) => {
//  evt.target.classList.add(`selected`);
//});
//
////Начало действия перемещения пилотов
//PilotsListElement.addEventListener(`dragstart`, (evt) => {
//    evt.target.classList.add(`selected`);
//});
//
////Конец действия перемещения инструкторов
//InstructorsListElement.addEventListener(`dragend`, (evt) => {
//    const activeElement = InstructorsListElement.querySelector(`.selected`);
//    const currentElement = document.elementFromPoint(event.clientX, event.clientY);
//    evt.target.classList.remove(`selected`);
//    console.log(currentElement.parentNode.classList);
//    if (!currentElement.parentNode.classList.contains(`test-flex`)) {return;}
//    //currentElement.parentNode.replaceChild(activeElement,currentElement);
//    currentElement.className=activeElement.className;
//    currentElement.innerHTML =activeElement.innerHTML;
//    currentElement.draggable = true;
//});
//
////Конец действия перемещения пилотов
//PilotsListElement.addEventListener(`dragend`, (evt) => {
//    const activeElement = PilotsListElement.querySelector(`.selected`);
//    const currentElement = document.elementFromPoint(event.clientX, event.clientY);
//    evt.target.classList.remove(`selected`);
//    console.log(currentElement.parentNode.classList);
//    if (!currentElement.parentNode.classList.contains(`test-flex`)) {return;}
//    //currentElement.parentNode.replaceChild(activeElement,currentElement);
//    currentElement.className=activeElement.className;
//    currentElement.innerHTML =activeElement.innerHTML;
//    currentElement.draggable = true;
//});
//
////Инициализация родительских классов элементов активной таблицы
//PeopleTableListElement = document.getElementById('followers');
//
////Инициализация списка всех элементов
//const peopleElements= PeopleTableListElement.querySelectorAll('.test-flex');
//
//
////Начало действия перемещения людей в таблице
//peopleElements.forEach(p => p.addEventListener(`dragstart`, (evt) => {
//    evt.target.classList.add(`selected`);
//}));
//
////Конец действия перемещения людей в таблице
//peopleElements.forEach(p => p.addEventListener(`dragend`, (evt) => {
//    evt.target.classList.remove(`selected`);
//    for (const inst of p.children) {
//        inst.classList.remove(`selected`);
//}
//}));
//
////Замена людей
//peopleElements.forEach(p => p.addEventListener(`dragover`, (evt) => {
//    // Разрешаем сбрасывать элементы в эту область
//    evt.preventDefault();
//
//    // Находим перемещаемый элемент
//    const activeElement = p.querySelector(`.selected`);
//    // Находим элемент, над которым в данный момент находится курсор
//    const currentElement = document.elementFromPoint(event.clientX, event.clientY);
//    // Проверяем, что событие сработало:
//    // 1. не на том элементе, который мы перемещаем,
//    // 2. именно на элементе списка
//    const isMoveable = activeElement !== currentElement &&
//    currentElement.classList.contains(`people`) && !currentElement.classList.contains(`selected`);
//
//    // Если нет, прерываем выполнение функции
//    if (!isMoveable) {
//    return;
//  }
//
//  // Находим элемент, перед которым будем вставлять
//    const nextElement = (currentElement === activeElement.nextElementSibling) ?
//      currentElement.nextElementSibling :
//      currentElement;
//
//   // Вставляем activeElement перед nextElement
//    //p.insertBefore(activeElement, nextElement);
//    const tmp=activeElement.innerHTML;
//    activeElement.innerHTML=currentElement.innerHTML;
//    currentElement.innerHTML=tmp;
//    activeElement.classList.remove(`selected`);
//    currentElement.classList.add(`selected`);
//}));