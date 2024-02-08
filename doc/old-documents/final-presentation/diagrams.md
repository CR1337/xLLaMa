# Diagrams


## Architecture

```mermaid
flowchart LR
    subgraph Frontend
        vue[Vue.js<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Vue.js_Logo_2.svg/1024px-Vue.js_Logo_2.svg.png">]
    end
    subgraph Database Interface
        flask-di[Flask<image src="https://flask-training-courses.uk/images/flask-logo.png">]
        peewee[Peewee<image src="https://docs.peewee-orm.com/en/latest/_images/peewee3-logo.png">]
    end
    subgraph Database
        postgres[(Postgres<image src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Postgresql_elephant.svg/1985px-Postgresql_elephant.svg.png">)]
    end
    subgraph code-analyzer[Code Analyzer]
        flask-ca[Flask<image src="https://flask-training-courses.uk/images/flask-logo.png">]
        pygments[Pygments<image src="https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fit-gro.github.io%2Fhugo-theme-w3css-basic.github.io%2Fresources%2Fimages%2Fteaserpics%2Fbitbucket.org%2Fpygments-main-logo_hu83f454384722f2ac083918ae2d1f75df_15959_800x0_resize_box_3.png&f=1&nofb=1&ipt=872c769311d235d625b4f5f4ef04111f01e31537b130c4fc8e4f0f1709798ac7&ipo=images">]
        ast[ast<image src="https://logos-download.com/wp-content/uploads/2016/10/Python_logo_icon.png">]
    end
    subgraph llm-facade-nginx[LLM Facade Nginx]
        nginx[Nginx<image src="https://logodownload.org/wp-content/uploads/2018/03/nginx-logo-3.png">]
    end
    subgraph llm-facade[LLM Facade]
        flask-lf[Flask<image src="https://flask-training-courses.uk/images/flask-logo.png">]
    end
    subgraph Ollama
        ollama[Ollama<image src="https://ollama.ai/public/ollama.png">]
    end
    subgraph Cache
        redis[Redis<image src="https://res.cloudinary.com/practicaldev/image/fetch/s--gWwIv4vV--/c_limit%2Cf_auto%2Cfl_progressive%2Cq_auto%2Cw_880/https://thepracticaldev.s3.amazonaws.com/i/787xlgwc2hhq3ctzxcvs.png">]
    end
    openai{{OpenAI<image src="https://www.pngitem.com/pimgs/m/66-668806_openai-logo-openai-logo-elon-musk-hd-png.png">}}

    flask-ca --- pygments
    flask-ca --- ast

    flask-di --- peewee

    vue --- flask-ca
    vue --- flask-di
    vue --- nginx
    nginx --- flask-lf

    peewee --- postgres

    flask-lf --- flask-di
    flask-lf --- openai
    flask-lf --- ollama
    flask-lf --- redis

    flask-ca --- flask-di

```

## Simple generation full

```mermaid
sequenceDiagram
    autonumber

    participant FE as Frontend
    participant LF as LLM Facade
    participant OL as Ollama
    participant CA as Code Analyzer
    participant DI as Database Interface

    FE ->>+ LF: GET /generate
        LF ->>+ OL: GET /api/generate
        OL -->>- LF: generated text
        LF ->>+ DI: POST /predictions
        DI -->>- LF: prediction_id
    LF -->>- FE: prediction_id

    FE ->>+ DI: GET /predictions/prediction_id
    DI -->>- FE: prediction

    FE ->>+ CA: GET /analyze-prediction?prediction=prediction_id
        CA ->>+ DI: GET /predictions/prediction_id
        DI -->>- CA: prediction
        par
            CA ->>+ DI: POST /code_snippets
            DI -->>- CA: code_snippet_id
        end
    CA -->>- FE: code_snippet_ids

    par
        FE ->>+ DI: GET /code_snippets/code_snippet_id
        DI -->>- FE: code_snippet
    end

    par
        FE ->>+ CA: GET /highlight?code_snippet=code_snippet_id
            CA ->>+ DI: GET /code_snippets/code_snippet_id
            DI -->>- CA: code_snippet
        CA -->>- FE: highlighted_code
    end
```

## Simple generation simplified

```mermaid
sequenceDiagram
    autonumber

    participant FE as Frontend
    participant LF as LLM Facade
    participant OL as Ollama
    participant CA as Code Analyzer

    FE ->>+ LF: GET /generate
        LF ->>+ OL: GET /api/generate
        OL -->>- LF: generated text
    LF -->>- FE: prediction

    FE ->>+ CA: GET /analyze-prediction?prediction=prediction
    CA -->>- FE: code_snippets

    par
        FE ->>+ CA: GET /highlight?code_snippet=code_snippet
        CA -->>- FE: highlighted_code
    end
```