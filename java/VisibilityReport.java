import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/**
 * Reads the CSV written by tracker/report.py --csv and prints one line per surface
 * (claude, ai_overview, ...) with mention rate, citation rate and share of voice.
 *
 *   javac -d out java/VisibilityReport.java
 *   java -cp out VisibilityReport examples/sample-runs.csv
 *
 * Java 17 or newer, standard library only.
 */
public class VisibilityReport {

    record Run(String date, String surface, String prompt, boolean mentioned, boolean cited, int rivals) {}

    static final class Tally {
        int runs, mentions, citations, rivalMentions;

        void add(Run r) {
            runs++;
            if (r.mentioned()) mentions++;
            if (r.cited()) citations++;
            rivalMentions += r.rivals();
        }

        double mentionRate() { return runs == 0 ? 0 : (double) mentions / runs; }

        double citationRate() { return runs == 0 ? 0 : (double) citations / runs; }

        /** Share of voice: brand mentions out of all brand and competitor mentions. */
        double shareOfVoice() {
            int total = mentions + rivalMentions;
            return total == 0 ? 0 : (double) mentions / total;
        }
    }

    /** Splits one CSV line, honouring double quotes and doubled quotes inside a field. */
    static List<String> splitCsv(String line) {
        List<String> out = new ArrayList<>();
        StringBuilder cur = new StringBuilder();
        boolean quoted = false;
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (quoted) {
                if (c == '"' && i + 1 < line.length() && line.charAt(i + 1) == '"') {
                    cur.append('"');
                    i++;
                } else if (c == '"') {
                    quoted = false;
                } else {
                    cur.append(c);
                }
            } else if (c == '"') {
                quoted = true;
            } else if (c == ',') {
                out.add(cur.toString());
                cur.setLength(0);
            } else {
                cur.append(c);
            }
        }
        out.add(cur.toString());
        return out;
    }

    static Run parse(String line) {
        List<String> f = splitCsv(line);
        String rivals = f.size() > 5 ? f.get(5) : "";
        int rivalCount = rivals.isBlank() ? 0 : rivals.split("\\|").length;
        return new Run(f.get(0), f.get(1), f.get(2), Boolean.parseBoolean(f.get(3)),
                Boolean.parseBoolean(f.get(4)), rivalCount);
    }

    static Map<String, Tally> summarize(List<String> lines) {
        Map<String, Tally> bySurface = new TreeMap<>();
        for (String line : lines.subList(1, lines.size())) {
            if (line.isBlank()) continue;
            Run r = parse(line);
            bySurface.computeIfAbsent(r.surface(), k -> new Tally()).add(r);
        }
        return bySurface;
    }

    public static void main(String[] args) throws IOException {
        if (args.length != 1) {
            System.err.println("usage: VisibilityReport <runs.csv>");
            System.exit(2);
        }
        List<String> lines = Files.readAllLines(Path.of(args[0]), StandardCharsets.UTF_8);
        System.out.printf("%-14s %5s %9s %9s %9s%n", "surface", "runs", "mention", "cited", "SoV");
        summarize(lines).forEach((surface, t) -> System.out.printf(
                "%-14s %5d %8.1f%% %8.1f%% %8.1f%%%n",
                surface, t.runs, t.mentionRate() * 100, t.citationRate() * 100, t.shareOfVoice() * 100));
    }
}
