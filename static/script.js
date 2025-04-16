let token = localStorage.getItem('token');

async function fetchWithAuth(url, options = {}) {
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
    };

    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
        return;
    }
    return response;
}

document.getElementById('itemForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('title').value;
    const description = document.getElementById('description').value;

    try {
        const response = await fetchWithAuth('/api/items/', {
            method: 'POST',
            body: JSON.stringify({
                title: title,
                description: description
            })
        });

        if (response.ok) {
            const item = await response.json();
            addItemToList(item);
            document.getElementById('itemForm').reset();
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to create item');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while creating the item');
    }
});

function addItemToList(item) {
    const itemsList = document.getElementById('itemsList');
    const itemElement = document.createElement('div');
    itemElement.className = 'item';
    itemElement.dataset.id = item.id;
    
    itemElement.innerHTML = `
        <div class="item-content">
            <h3>${item.title}</h3>
            <p>${item.description}</p>
        </div>
        <div class="item-actions">
            <button class="edit-btn">Edit</button>
            <button class="delete-btn">Delete</button>
        </div>
    `;
    
    itemsList.appendChild(itemElement);
    setupItemListeners(itemElement);
}

function setupItemListeners(itemElement) {
    const id = itemElement.dataset.id;
    
    itemElement.querySelector('.edit-btn').addEventListener('click', async () => {
        const title = prompt('Enter new title:', itemElement.querySelector('h3').textContent);
        const description = prompt('Enter new description:', itemElement.querySelector('p').textContent);
        
        if (title && description) {
            try {
                const response = await fetchWithAuth(`/api/items/${id}`, {
                    method: 'PUT',
                    body: JSON.stringify({
                        title: title,
                        description: description
                    })
                });

                if (response.ok) {
                    const item = await response.json();
                    itemElement.querySelector('h3').textContent = item.title;
                    itemElement.querySelector('p').textContent = item.description;
                } else {
                    const error = await response.json();
                    alert(error.detail || 'Failed to update item');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while updating the item');
            }
        }
    });

    itemElement.querySelector('.delete-btn').addEventListener('click', async () => {
        if (confirm('Are you sure you want to delete this item?')) {
            try {
                const response = await fetchWithAuth(`/api/items/${id}`, {
                    method: 'DELETE'
                });

                if (response.ok) {
                    itemElement.remove();
                } else {
                    const error = await response.json();
                    alert(error.detail || 'Failed to delete item');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while deleting the item');
            }
        }
    });
}

document.getElementById('logoutBtn').addEventListener('click', async () => {
    try {
        const response = await fetchWithAuth('/logout', {
            method: 'POST'
        });

        if (response.ok) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to logout');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while logging out');
    }
});

// Load items when page loads
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetchWithAuth('/api/items/');
        if (response.ok) {
            const items = await response.json();
            items.forEach(item => addItemToList(item));
        } else {
            const error = await response.json();
            alert(error.detail || 'Failed to load items');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while loading items');
    }
}); 