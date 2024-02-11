export const debug = {
    explanationText:`# xLLaMa

## Setup

### 1. Install Docker
See [Docker Installation](https://docs.docker.com/engine/install/) (if not already installed)

### 2. Install Python 3
Install at least Python 3.10 with Pip (if not already installed). Earlier versions might work but are not tested.

### 3. Clone this Repository
\`\`\`bash
git clone https://github.com/CR1337/xLLaMa.git
\`\`\`

### 4. Change into the Repository
\`\`\`bash
cd xLLaMa
\`\`\`

### 5. Create a virtual environment (optional)
\`\`\`bash
python3 -m venv .venv
\`\`\`

### 6. Activate the virtual environment (optional)
\`\`\`bash
source .venv/bin/activate
\`\`\`

### 7. Run setup script
If you are on the production server with GPUs 2 and 3, run
\`\`\`bash
bin/setup
\`\`\`
else run
\`\`\`bash
bin/setup-local
\`\`\`

## Usage
### 1. Run the application
For running in the background (recommended for production):
\`\`\`bash
bin/run
\`\`\`
For seeing terminal output (recommended for development):
\`\`\`bash
bin/run-blocking
\`\`\`

If you are not on the production server with GPUs 2 and 3 use
\`\`\`bash
bin/run-local
\`\`\`
or
\`\`\`bash
bin/run-blocking-local
\`\`\`
respectively.

### 2. Open the application
Open the application in a browser at http://localhost:8080. You can replace localhost with the IP of the server.

### 3. Stop the application
\`\`\`bash
bin/stop
\`\`\`
or if you are not on the production server with GPUs 2 and 3
\`\`\`bash
bin/stop-local
\`\`\`
`,

    codeSnippetHtml:`<div class="highlight"><pre><span></span><span class="kn">from</span> <span class="nn">transformers</span> <span class="kn">import</span> <span class="n">AutoTokenizer</span><span class="p">,</span> <span class="n">BertTokenizerFast</span>
<span class="kn">import</span> <span class="nn">torch</span>
<span class="n">tokenizer</span> <span class="o">=</span> <span class="n">AutoTokenizer</span><span class="o">.</span><span class="n">from_pretrained</span><span class="p">(</span><span class="s2">"bert-base-uncased"</span><span class="p">)</span>
<span class="n">sequences</span> <span class="o">=</span> <span class="p">[</span><span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'encode')">encode</a></u></b></span><span class="p">(</span><span class="s2">"This is a test"</span><span class="p">,</span> <span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'add_special_tokens')">add_special_tokens</a></u></b></span><span class="o">=</span><span class="kc">False</span><span class="p">),</span> <span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'encode')">encode</a></u></b></span><span class="p">(</span><span class="s2">"Another sentence"</span><span class="p">,</span> <span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'add_special_tokens')">add_special_tokens</a></u></b></span><span class="o">=</span><span class="kc">False</span><span class="p">)]</span>
<span class="n">batch_decoded</span> <span class="o">=</span> <span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'batch_decode')">batch_decode</a></u></b></span><span class="p">(</span><span class="n">sequences</span><span class="p">)</span>
<span class="nb">print</span><span class="p">(</span><span class="n">batch_decoded</span><span class="p">)</span> <span class="c1"># Output: ['this is a test', 'another sentence']</span>
<span class="c1"># Convert the sequences to tensors and pass them through the model</span>
<span class="n">input_ids</span> <span class="o">=</span> <span class="n">torch</span><span class="o">.</span><span class="n">tensor</span><span class="p">([</span><span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'encode')">encode</a></u></b></span><span class="p">(</span><span class="s2">"This is a test"</span><span class="p">,</span> <span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'add_special_tokens')">add_special_tokens</a></u></b></span><span class="o">=</span><span class="kc">False</span><span class="p">),</span> <span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'encode')">encode</a></u></b></span><span class="p">(</span><span class="s2">"Another sentence"</span><span class="p">,</span> <span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'add_special_tokens')">add_special_tokens</a></u></b></span><span class="o">=</span><span class="kc">False</span><span class="p">)])</span>
<span class="n">outputs</span> <span class="o">=</span> <span class="n">model</span><span class="p">(</span><span class="n">input_ids</span><span class="p">)</span>
<span class="c1"># Use the 'batch_decode' method to decode the output ids</span>
<span class="n">decoded_sequences</span> <span class="o">=</span> <span class="n">tokenizer</span><span class="o">.</span><span class="n"><b><u><a class="clickable" onclick="handleCodeSnippetObjectClick('3330b658-b5b1-4723-aa5c-0a0f48c51121', 'batch_decode')">batch_decode</a></u></b></span><span class="p">(</span><span class="n">outputs</span><span class="p">[</span><span class="mi">0</span><span class="p">],</span> <span class="n">skip_special_tokens</span><span class="o">=</span><span class="kc">True</span><span class="p">,</span> <span class="n">clean_up_tokenization_spaces</span><span class="o">=</span><span class="kc">False</span><span class="p">)</span>
<span class="nb">print</span><span class="p">(</span><span class="n">decoded_sequences</span><span class="p">)</span> <span class="c1"># Output: ['this is a test', 'another sentence']</span>
</pre></div>
`,

    prefixWrapperText: "This is some text.",

    suffixWrapperText: `This is some more text that is a bit longer and has more lines.
Once upon a time there was a very long text with multiple lines that was so long that it was too long.
This is some more text that is a bit longer and has more lines.
`
};
