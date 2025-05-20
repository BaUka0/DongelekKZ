document.addEventListener('DOMContentLoaded', function() {
    const brandSelect = document.getElementById('id_brand');
    const modelSelect = document.getElementById('id_model');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Инициализация модальных окон
    const brandModal = document.getElementById('brand-modal');
    const modelModal = document.getElementById('model-modal');
    const addBrandButton = document.getElementById('add-brand-button');
    const addModelButton = document.getElementById('add-model-button');
    const saveBrandButton = document.getElementById('save-brand-button');
    const saveModelButton = document.getElementById('save-model-button');
    const modalCloseButtons = document.querySelectorAll('.modal-close, .modal-cancel');
    
    const brandAlert = document.getElementById('brand-alert');
    const modelAlert = document.getElementById('model-alert');
    
    // Add form-control class to all form fields if not already added by Django
    document.querySelectorAll('input, select, textarea').forEach(el => {
        if (!el.classList.contains('form-control') && el.type !== 'hidden' && el.type !== 'submit' && el.type !== 'button') {
            el.classList.add('form-control');
        }
    });
    
    // Загрузка моделей при изменении бренда
    brandSelect.addEventListener('change', function() {
        loadModelsByBrand(this.value);
    });
    
    // Функция загрузки моделей для выбранного бренда
    function loadModelsByBrand(brandId) {
        if (!brandId) {
            // Очистка селекта моделей если бренд не выбран
            modelSelect.innerHTML = '<option value="">---------</option>';
            modelSelect.disabled = true;
            return;
        }
        
        modelSelect.disabled = true;
        modelSelect.innerHTML = '<option value="">Жүктелуде...</option>';
        
        fetch(`/api/models/?brand=${brandId}`)
            .then(response => response.json())
            .then(data => {
                modelSelect.innerHTML = '<option value="">Модельді таңдаңыз</option>';
                
                data.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    modelSelect.appendChild(option);
                });
                
                modelSelect.disabled = false;
            })
            .catch(error => {
                console.error('Модельдерді жүктеу кезіндегі қате:', error);
                modelSelect.innerHTML = '<option value="">Қате орын алды</option>';
                modelSelect.disabled = true;
            });
    }
    
    // Открытие модального окна добавления бренда
    addBrandButton.addEventListener('click', function() {
        document.getElementById('brand-name').value = '';
        brandAlert.style.display = 'none';
        brandModal.style.display = 'block';
    });
    
    // Открытие модального окна добавления модели
    addModelButton.addEventListener('click', function() {
        document.getElementById('model-brand').value = brandSelect.value;
        document.getElementById('model-name').value = '';
        modelAlert.style.display = 'none';
        modelModal.style.display = 'block';
    });
    
    // Закрытие модальных окон
    modalCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            brandModal.style.display = 'none';
            modelModal.style.display = 'none';
        });
    });
    
    // Закрытие модальных окон при клике вне области
    window.addEventListener('click', function(event) {
        if (event.target === brandModal) {
            brandModal.style.display = 'none';
        }
        if (event.target === modelModal) {
            modelModal.style.display = 'none';
        }
    });
    
    // Сохранение нового бренда
    saveBrandButton.addEventListener('click', function() {
        const brandName = document.getElementById('brand-name').value.trim();
        
        if (!brandName) {
            showAlert(brandAlert, 'Бренд атауын енгізіңіз!', 'danger');
            return;
        }
        
        fetch('/api/brands/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `name=${encodeURIComponent(brandName)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Добавление нового бренда в селект
                const option = document.createElement('option');
                option.value = data.id;
                option.textContent = data.name;
                brandSelect.appendChild(option);
                
                // Выбор нового бренда
                brandSelect.value = data.id;
                
                // Обновление селекта моделей
                loadModelsByBrand(data.id);
                
                // Обновление селекта брендов в модальном окне моделей
                const modelBrandSelect = document.getElementById('model-brand');
                const modelBrandOption = document.createElement('option');
                modelBrandOption.value = data.id;
                modelBrandOption.textContent = data.name;
                modelBrandSelect.appendChild(modelBrandOption);
                
                showAlert(brandAlert, 'Жаңа бренд сәтті қосылды!', 'success');
                
                // Закрытие модального окна через 1 секунду
                setTimeout(() => {
                    brandModal.style.display = 'none';
                }, 1000);
            } else {
                showAlert(brandAlert, 'Қате: ' + Object.values(data.errors).join(', '), 'danger');
            }
        })
        .catch(error => {
            console.error('Брендті сақтау кезіндегі қате:', error);
            showAlert(brandAlert, 'Серверде қате орын алды', 'danger');
        });
    });
    
    // Сохранение новой модели
    saveModelButton.addEventListener('click', function() {
        const brandId = document.getElementById('model-brand').value;
        const modelName = document.getElementById('model-name').value.trim();
        
        if (!brandId) {
            showAlert(modelAlert, 'Брендті таңдаңыз!', 'danger');
            return;
        }
        
        if (!modelName) {
            showAlert(modelAlert, 'Модель атауын енгізіңіз!', 'danger');
            return;
        }
        
        fetch('/api/models/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `name=${encodeURIComponent(modelName)}&brand=${encodeURIComponent(brandId)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Если текущий выбранный бренд совпадает с брендом новой модели
                if (brandSelect.value === data.brand_id.toString()) {
                    // Добавление новой модели в селект
                    const option = document.createElement('option');
                    option.value = data.id;
                    option.textContent = data.name;
                    modelSelect.appendChild(option);
                    
                    // Выбор новой модели
                    modelSelect.value = data.id;
                } else {
                    // Если бренды не совпадают, обновляем выбранный бренд
                    brandSelect.value = data.brand_id;
                    loadModelsByBrand(data.brand_id);
                    
                    // После загрузки моделей выбираем новую модель
                    setTimeout(() => {
                        modelSelect.value = data.id;
                    }, 500);
                }
                
                showAlert(modelAlert, 'Жаңа модель сәтті қосылды!', 'success');
                
                // Закрытие модального окна через 1 секунду
                setTimeout(() => {
                    modelModal.style.display = 'none';
                }, 1000);
            } else {
                showAlert(modelAlert, 'Қате: ' + Object.values(data.errors).join(', '), 'danger');
            }
        })
        .catch(error => {
            console.error('Модельді сақтау кезіндегі қате:', error);
            showAlert(modelAlert, 'Серверде қате орын алды', 'danger');
        });
    });
    
    // Функция отображения уведомлений
    function showAlert(element, message, type) {
        element.textContent = message;
        element.className = 'alert alert-' + type;
        element.style.display = 'block';
    }
    
    // Инициализация моделей для выбранного бренда при загрузке страницы
    if (brandSelect.value) {
        loadModelsByBrand(brandSelect.value);
    }
    
    // Отключение селекта моделей, если бренд не выбран
    if (!brandSelect.value) {
        modelSelect.disabled = true;
    }

    // Обработка предварительного просмотра изображения
    const imageInput = document.getElementById('id_image');
    if (imageInput) {
        imageInput.addEventListener('change', function(event) {
            const fileInput = event.target;
            const fileInfo = document.querySelector('.file-info');
            const preview = document.getElementById('image-preview');
            
            if (fileInput.files && fileInput.files[0]) {
                const file = fileInput.files[0];
                fileInfo.textContent = file.name;
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.innerHTML = '';
                    preview.classList.remove('empty');
                    
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.alt = 'Алдын ала көрініс';
                    preview.appendChild(img);
                };
                reader.readAsDataURL(file);
            } else {
                fileInfo.textContent = 'Файл таңдалмаған';
                preview.innerHTML = '<span class="preview-text">Алдын ала көрініс</span>';
                preview.classList.add('empty');
            }
        });
    }
});
