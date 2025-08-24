import os
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Helpers
def _wait(context): return WebDriverWait(context.driver, getattr(context, "wait_seconds", 5))
def _id(context, eid): return _wait(context).until(EC.presence_of_element_located((By.ID, eid)))

FIELD_IDS = {
    "Id": "product_id",
    "Name": "name",
    "Description": "description",
    "Available": "available",
    "Category": "category",
    "Price": "price",
}

def _field_id(label): return FIELD_IDS.get(label, label)
def _set(elem, value):
    if elem.tag_name.lower() == "select":
        Select(elem).select_by_visible_text(value)
    else:
        elem.clear(); elem.send_keys(value)

def _get(elem):
    return Select(elem).first_selected_option.text.strip() if elem.tag_name.lower() == "select" else elem.get_attribute("value")

# Navegación
@when('I visit the "Home Page"')
def step_visit(context):
    url = getattr(context, "base_url", None) or os.getenv("UI_URL", "http://localhost:8080")
    context.driver.get(url)
    _wait(context).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

# Botón
@when('I press the "{button}" button')
def step_press(context, button):
    button_id = button.lower() + "-btn"
    _id(context, button_id).click()

# Set/Change/Select
@when('I set the "{field}" to "{value}"')
def step_set(context, field, value):
    _set(_id(context, _field_id(field)), value)

@when('I change "{field}" to "{value}"')
def step_change(context, field, value):
    _set(_id(context, _field_id(field)), value)

@when('I select "{value}" in the "{field}" dropdown')
def step_select(context, value, field):
    Select(_id(context, _field_id(field))).select_by_visible_text(value)

# Copy/Paste Id
@when('I copy the "{field}" field')
def step_copy(context, field):
    context._clipboard = _get(_id(context, _field_id(field)))

@when('I paste the "{field}" field')
def step_paste(context, field):
    elem = _id(context, _field_id(field))
    elem.clear(); elem.send_keys(getattr(context, "_clipboard", ""))

# Verificaciones de campos
@then('I should see "{text}" in the "{field}" field')
def step_see_in_field(context, text, field):
    actual = _get(_id(context, _field_id(field)))
    assert actual == text, f'Expected "{text}" in {field}, got "{actual}"'

@then('I should see "{text}" in the "{field}" dropdown')
def step_see_in_dropdown(context, text, field):
    actual = _get(_id(context, _field_id(field)))
    assert actual == text, f'Expected "{text}" in {field} dropdown, got "{actual}"'

# Resultados
@then('I should see "{name}" in the results')
def step_see_in_results(context, name):
    found = _wait(context).until(EC.text_to_be_present_in_element((By.ID, "search_results"), name))
    assert found

@then('I should not see "{name}" in the results')
def step_not_see_in_results(context, name):
    element = _id(context, "search_results")
    assert name not in element.text

# Mensajes
@then('I should see the message "{message}"')
def step_see_message(context, message):
    found = _wait(context).until(EC.text_to_be_present_in_element((By.ID, "flash_message"), message))
    assert found
