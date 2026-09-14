import Foundation
import Combine

struct Property: Codable, Identifiable {
    var id: String { link }
    let preco: Double
    let area: Double?
    let quartos: Int?
    let banheiros: Int?
    let vagas: Int?
    let bairro: String
    let cidade: String
    let uf: String
    let tipo: String
    let link: String
    let imobiliaria: String
    var neighborhood: String { bairro.replacingOccurrences(of: "_", with: " ") }
    var areaLabel: String { area.map { "\($0.formatted()) m²" } ?? "Área não informada" }
    var price: String { preco.formatted(.currency(code: "BRL").locale(Locale(identifier: "pt_BR"))) }
    var safeURL: URL? {
        guard let url = URL(string: link), ["https", "http"].contains(url.scheme?.lowercased() ?? ""), url.host != nil else { return nil }
        return url
    }
}

struct Catalog: Codable {
    let last_update: String
    let properties: [Property]
}

struct PropertyPage: Decodable {
    let total_pages: Int
    let last_update: String?
    let properties: [Property]
}

@MainActor
final class CatalogStore: ObservableObject {
    @Published var properties: [Property] = []
    @Published var lastUpdate = ""
    @Published var loading = false
    @Published var message: String?
    @Published var favorites: Set<String> {
        didSet { UserDefaults.standard.set(Array(favorites), forKey: "favorites") }
    }
    private let cache = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0].appendingPathComponent("catalog.json")

    init() {
        favorites = Set(UserDefaults.standard.stringArray(forKey: "favorites") ?? [])
        do {
            let bundled = Bundle.main.url(forResource: "catalog", withExtension: "json")!
            let url = FileManager.default.fileExists(atPath: cache.path) ? cache : bundled
            let catalog = try JSONDecoder().decode(Catalog.self, from: Data(contentsOf: url))
            properties = catalog.properties
            lastUpdate = catalog.last_update
        } catch { message = "Não foi possível carregar o catálogo local: \(error.localizedDescription)" }
    }

    func toggle(_ property: Property) {
        if favorites.contains(property.id) { favorites.remove(property.id) }
        else { favorites.insert(property.id) }
    }

    func refresh(baseAddress: String) async {
        guard !loading else { return }
        guard let base = URL(string: baseAddress.trimmingCharacters(in: .whitespacesAndNewlines)),
              ["http", "https"].contains(base.scheme?.lowercased() ?? ""), base.host != nil else {
            message = "Informe o endereço da API, por exemplo http://192.168.1.10:8000."
            return
        }
        loading = true
        defer { loading = false }
        do {
            func fetch(_ url: URL) async throws -> Data {
                var request = URLRequest(url: url)
                request.timeoutInterval = 15
                let (data, response) = try await URLSession.shared.data(for: request)
                guard let http = response as? HTTPURLResponse, http.statusCode == 200 else {
                    throw URLError(.badServerResponse)
                }
                return data
            }
            struct Cities: Decodable { let cities: [String] }
            let cities = try JSONDecoder().decode(Cities.self, from: await fetch(base.appendingPathComponent("api/cities")))
            var all: [String: Property] = [:]
            var update = lastUpdate
            for city in cities.cities {
                var page = 1
                while true {
                    var url = URLComponents(url: base.appendingPathComponent("api/properties"), resolvingAgainstBaseURL: false)!
                    url.queryItems = [URLQueryItem(name: "cidade", value: city), URLQueryItem(name: "page", value: String(page)), URLQueryItem(name: "per_page", value: "100")]
                    let result = try JSONDecoder().decode(PropertyPage.self, from: await fetch(url.url!))
                    for property in result.properties { all[property.id] = property }
                    update = result.last_update ?? update
                    if page >= result.total_pages { break }
                    page += 1
                }
            }
            let catalog = Catalog(last_update: update, properties: all.values.sorted { $0.preco < $1.preco })
            try JSONEncoder().encode(catalog).write(to: cache, options: .atomic)
            properties = catalog.properties
            lastUpdate = catalog.last_update
            message = "Catálogo atualizado: \(properties.count) imóveis."
        } catch { message = "Não foi possível atualizar. Seu catálogo offline foi preservado. \(error.localizedDescription)" }
    }
}
