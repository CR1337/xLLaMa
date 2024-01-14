import json
import re

def extract_function_info(func_str, doc_str):
    info = {
        "name": "",
        "url": "",
        "description": "",
        "source": ""
    }

    # Extracting name and url using regular expressions
    match = re.search(r'def\s+(\w+)\s*\(', func_str)
    if match:
        info["name"] = "tokenizer." + match.group(1)
        info["url"] = f"https://huggingface.co/docs/transformers/main_classes/tokenizer#transformers.PreTrainedTokenizer.{match.group(1)}"

    # Extracting docstring
    docstring = doc_str.strip()

    # Extracting source code (outside of docstring)
    source_code = func_str.strip()

    info["source"] = source_code

    # Splitting docstring into lines
    lines = [line.strip() for line in docstring.split('\n')]
    info["description"] = ' '.join(lines)

    return info

def append_to_json_file(info, filename):
    try:
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = []

    data.append(info)

    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Given function string
func_str = """
def tokenize(self, text: TextInput, **kwargs) -> List[str]:
        
        split_special_tokens = kwargs.pop("split_special_tokens", self.split_special_tokens)

        text, kwargs = self.prepare_for_tokenization(text, **kwargs)

        if kwargs:
            logger.warning(f"Keyword arguments {kwargs} not recognized.")

        if hasattr(self, "do_lower_case") and self.do_lower_case:
            # convert non-special tokens to lowercase. Might be super slow as well?
            escaped_special_toks = [re.escape(s_tok) for s_tok in (self.all_special_tokens)]
            escaped_special_toks += [
                re.escape(s_tok.content)
                for s_tok in (self._added_tokens_decoder.values())
                if not s_tok.special and s_tok.normalized
            ]
            pattern = r"(" + r"|".join(escaped_special_toks) + r")|" + r"(.+?)"
            text = re.sub(pattern, lambda m: m.groups()[0] or m.groups()[1].lower(), text)

        if split_special_tokens:
            no_split_token = []
            tokens = [text]
        else:
            no_split_token = self._added_tokens_encoder.keys()  # don't split on any of the added tokens
            # "This is something<special_token_1>  else"
            tokens = self.tokens_trie.split(text)

        # ["This is something", "<special_token_1>", "  else"]
        for i, token in enumerate(tokens):
            if token in no_split_token:
                tok_extended = self._added_tokens_decoder.get(self._added_tokens_encoder[token], None)
                left = tokens[i - 1] if i > 0 else None
                right = tokens[i + 1] if i < len(tokens) - 1 else None
                if isinstance(tok_extended, AddedToken):
                    if tok_extended.rstrip and right:
                        # A bit counter-intuitive but we strip the left of the string
                        # since tok_extended.rstrip means the special token is eating all white spaces on its right
                        tokens[i + 1] = right.lstrip()
                    # Strip white spaces on the left
                    if tok_extended.lstrip and left:
                        tokens[i - 1] = left.rstrip()  # Opposite here
                    if tok_extended.single_word and left and left[-1] != " ":
                        tokens[i - 1] += token
                        tokens[i] = ""
                    elif tok_extended.single_word and right and right[0] != " ":
                        tokens[i + 1] = token + tokens[i + 1]
                        tokens[i] = ""
                else:
                    raise ValueError(
                        f"{tok_extended} cannot be tokenized because it was not properly added"
                        f" to the tokenizer. This means that it is not an `AddedToken` but a {type(tok_extended)}"
                    )
        # ["This is something", "<special_token_1>", "else"]
        tokenized_text = []
        for token in tokens:
            # Need to skip eventual empty (fully stripped) tokens
            if not token:
                continue
            if token in no_split_token:
                tokenized_text.append(token)
            else:
                tokenized_text.extend(self._tokenize(token))
        # ["This", " is", " something", "<special_token_1>", "else"]
        return tokenized_text

"""

doc_str = """
        Converts a string in a sequence of tokens, using the tokenizer.

        Split in words for word-based vocabulary or sub-words for sub-word-based vocabularies
        (BPE/SentencePieces/WordPieces). Takes care of added tokens.

        Args:
            text (`str`):
                The sequence to be encoded.
            **kwargs (additional keyword arguments):
                Passed along to the model-specific `prepare_for_tokenization` preprocessing method.

        Returns:
            `List[str]`: The list of tokens.
        """

# Extracting information
function_info = extract_function_info(func_str, doc_str)

# Appending to the existing JSON file
json_filename = "huggingface_info.json"
append_to_json_file(function_info, json_filename)
print(f"Information appended to '{json_filename}' successfully.")
