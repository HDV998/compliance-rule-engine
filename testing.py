def check_transcation(transaction):
    if transaction['amount'] > 10000:
        print("high value transaction")
    else:
        print("normal")
        
def apply_rule(transaction, rule):
    op = rule["operator"]
    value = rule["value"]
    
    field_value = transaction.get(rule['field'])
    
    if field_value is None:
        raise ValueError("please enter a category to compare with")
    
    if op == ">":
        return field_value > value
    elif op == "<":
        return field_value < value
    elif op == "==":
        return field_value == value
    elif op == ">=":
        return field_value >= value
    elif op == "<=":
        return field_value <= value
    else:
        raise ValueError("Invalid operator")
    
def apply_rules(transaction, rules): #works only for AND operation of rules
    for rule in rules:
        if not apply_rule(transaction, rule):
            return False
        
    return True

def evaluate_rules(transaction, rules):
    rule_type = rules["type"]
    sub_rules = rules["rules"]
    
    results = []
    
    for r in sub_rules:
        if "type" in r:
            results.append(evaluate_rules(transaction, r))
        else:
            results.append(apply_rule(transaction, r))
    
    if len(results) == 0:
        raise ValueError("the results array is empty")
    if rule_type == "AND":
        return all(results)
    elif rule_type == "OR":
        return any(results)
    elif rule_type == "NOT":
        return not(results[0])
    else:
        raise ValueError("incorrect Operator provided")
            
        
        
rule = {"field": "country", "operator": "==", "value": "India"}

rule1 = {"field": "amount", "operator": ">", "value": 10000}
rule2 = {"field": "country", "operator": "==", "value": "India"} 

rules = [rule1, rule2]

transaction = {"amount": 12000, "country": "India"}

Rules = {
    "type": "OR",
    "rules": [
        {
            "type": "AND",
            "rules": [
                {"field": "amount", "operator": ">", "value": 10000},
                {"field": "country", "operator": "==", "value": "India"}
            ]
        },
        {"field": "amount", "operator": "<", "value": 1000}
    ]
}
print(evaluate_rules(transaction, Rules))