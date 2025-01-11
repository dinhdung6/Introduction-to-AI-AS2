import sys
from logic import *
from truthtable import TruthTable
from forward_chaining import ForwardChaining
from backward_chaining import BackwardChaining
from Reader import read, extract_symbols_and_sentences
from sentence_transformers import create_knowledge_base, parse
from DPLL import DPLL

def main():
    # Ensure proper usage of the script
    if len(sys.argv) != 3:
        print("Usage: python iengine.py <filename> <method>")
        sys.exit(1)

    filename = sys.argv[1]
    method = sys.argv[2].upper()

    # Step 1: Read the knowledge base and the query
    tell, query = read(filename)
    print(f'Tell: {tell}')
    print(f'Query/Ask: {query}\n')

    # Extract symbols and sentences from the knowledge base
    symbols, sentences = extract_symbols_and_sentences(tell)
    print(f'Symbols: {symbols}')
    print(f'Sentence: {sentences}\n')

    # Step 2: Create symbol objects and knowledge base
    symbol_objects = {symbol: Symbol(symbol) for symbol in symbols}
    knowledge_base = create_knowledge_base(sentences)
    query_sentence = parse(query)

    # Debugging information
    print(f'Knowledge Base: {knowledge_base}')
    print(f'Query Sentence: {query_sentence}\n')

    # Step 3: Choose method and solve
    if method == "MC":
        is_valid = model_check(knowledge_base, query_sentence)
        print(f'Model Check Result: {"YES" if is_valid else "NO"}')

    elif method == "FC":
        fc = ForwardChaining(knowledge_base, query_sentence)
        fc_result = fc.solve()
        print(f'Forward Chaining Result: {fc_result}')

    elif method == "BC":
        bc = BackwardChaining(knowledge_base, query_sentence)
        bc_result = bc.solve()
        print(f'Backward Chaining Result: {bc_result}')

    elif method == "TT":
        tt = TruthTable(symbols, knowledge_base, query_sentence)
        print(tt)
        result = tt.get_entailed_symbols()
        print(f'Truth Table Result: {result}')

    elif method == "DPLL":
        dpll = DPLL(knowledge_base, query_sentence)
        dpll_result = dpll.solve()
        print(f'DPLL Result: {dpll_result}')

    else:
        print("Invalid method. Available methods: MC (Model Check), FC (Forward Chaining), BC (Backward Chaining), TT (Truth Table), DPLL")
        sys.exit(1)

if __name__ == "__main__":
    main()