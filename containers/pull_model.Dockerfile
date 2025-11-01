FROM ollama/ollama:latest AS ollama
FROM babashka/babashka:latest

COPY --from=ollama /bin/ollama ./bin/ollama

COPY <<EOF pull_model.clj
(ns pull-model
  (:require [babashka.process :as process]
            [clojure.core.async :as async]))

(try
  (let [llm (System/getenv "LLM")
        url (System/getenv "OLLAMA_BASE_URL")]
    (println (format "Pulling Ollama model %s using %s" llm url))
    (when (and llm url)
      (let [done (async/chan)]
        (async/go-loop [n 0]
          (let [[v _] (async/alts! [done (async/timeout 5000)])]
            (if (= :stop v)
              :stopped
              (do
                (println (format "... pulling model (%ss) - may take a few minutes" (* n 5)))
                (recur (inc n))))))
        (process/shell {:env {"OLLAMA_HOST" url "HOME" (System/getProperty "user.home")}
                        :out :inherit
                        :err :inherit}
                       (format "./bin/ollama show %s --modelfile > /dev/null || ./bin/ollama pull %s" llm llm))
        (async/>!! done :stop))))
  (catch Throwable e
    (println "Error:" e)
    (System/exit 1)))
EOF

ENTRYPOINT ["bb", "-f", "pull_model.clj"]