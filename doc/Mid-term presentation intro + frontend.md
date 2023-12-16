Letztes Mal haben wir euch von Luisa erzählt, einer Softwareentwicklerin, die sich ein Tool zur Generierung von Codebeispielen wünscht, mit dem sie schneller und einfacher relevante Beispiele vorgeschlagen bekommt, ohne zunächst längere Unterhaltungen mit dem LLM führen zu müssen. 

Wir haben das Tool in Form einer Webanwendung entwickelt, um eine längerfristige und bessere Kompatibilität zu gewährleisten. 

Zur Zeit können nur Beispiele für pandas generiert werden, allerdings lässt sich die Anwendung mit der Zeit für beliebig viele weitere Frameworks und APIs erweitern. 
Man wählt die gewünschte Funktion aus, für die ein Beispiel generiert werden soll, entweder frei oder aus einer Liste von Vorschlägen. Diese können festgelegt oder anhand von gesammelten Daten vorgeschlagen werden. 

Damit das Beispiel besser auf einen bestimmten Kontext zugeschnitten ist, kann man eigenen Code eingeben, der bei der Generierung berücksichtigt wird.
Um außerdem eine möglichst gute Auswahl von Beispielen zu ermöglichen und den Prozess weiter zu beschleunigen, wird das Beispiel von mehreren Models gleichzeitig generiert. 

Nach der Generierung kann man sich das Beispiel erklären lassen, oder eine erneute Generierung anhand von Feedback anregen. 

Kommen im generierten Beispiel weitere Funktionen vor, die man nicht kennt, kann man diese einfach auswählen und auch diese erklären oder sich ein Beispiel dafür generieren lassen.

Unser Ziel ist es, einen guten Kompromiss aus Geschwindigkeit und Qualität zu finden. Die Generierung soll möglichst schnell mit nur wenigen Klicks geschehen, die Qualität des Beispiels soll allerdings hoch genug sein, damit die Beispiele tatsächlich hilfreich sind. 
