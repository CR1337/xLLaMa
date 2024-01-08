Letztes Mal haben wir euch von Luisa erzählt, einer Softwareentwicklerin, die sich ein Tool zur Generierung von Codebeispielen wünscht, mit dem sie schneller und einfacher relevante Beispiele vorgeschlagen bekommt, ohne zunächst längere Unterhaltungen mit dem LLM führen zu müssen. 

Wir haben das Tool in Form einer Webanwendung entwickelt, um eine längerfristige und bessere Kompatibilität zu gewährleisten. 

Zur Zeit können nur Beispiele für pandas generiert werden, allerdings lässt sich die Anwendung mit der Zeit für beliebig viele weitere Frameworks und APIs erweitern. 
Man wählt die gewünschte Funktion aus, für die ein Beispiel generiert werden soll, entweder frei oder aus einer Liste von Vorschlägen. Falls die Zeit ausreicht, würden wir diese Liste gern dynamischer generieren.
Um eine möglichst gute Auswahl von Beispielen zu ermöglichen und den Prozess weiter zu beschleunigen, wird das Beispiel von mehreren Modellen gleichzeitig generiert. 

Nach der Generierung kann man sich das Beispiel erklären lassen, oder eine erneute Generierung anhand von Feedback anregen. Es soll außerdem möglich sein, sich Funktionen direkt aus dem Beispiel auszuwählen und auch zu ihnen ein Beispiel zu generieren. Daran arbeiten wir derzeit noch, der Grundbaustein im Backend ist allerdings bereits gelegt.

Unser Ziel ist es, einen guten Kompromiss aus Geschwindigkeit und Qualität zu finden. Die Generierung soll möglichst schnell mit nur wenigen Klicks geschehen, die Qualität des Beispiels soll allerdings hoch genug sein, damit die Beispiele tatsächlich hilfreich sind. Wir können dies am besten an uns selbst testen, indem wir das Tool während unserer Arbeit benutzen.

Zu unseren größten Herausforderungen gehörte bislang die Verbindung von Frontend und Backend. -> evtl auch im Backend Text nennen.
