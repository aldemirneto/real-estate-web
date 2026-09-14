import SwiftUI

@main
struct RealEstateApp: App {
    @StateObject private var store = CatalogStore()
    var body: some Scene {
        WindowGroup {
            TabView {
                CatalogView(favoritesOnly: false).tabItem { Label("Explorar", systemImage: "building.2") }
                CatalogView(favoritesOnly: true).tabItem { Label("Favoritos", systemImage: "heart") }
                SettingsView().tabItem { Label("Ajustes", systemImage: "gearshape") }
            }
            .tint(Color(red: 0.08, green: 0.45, blue: 0.37))
            .environmentObject(store)
        }
    }
}

struct CatalogView: View {
    @EnvironmentObject var store: CatalogStore
    @AppStorage("apiAddress") private var apiAddress = "http://localhost:8000"
    let favoritesOnly: Bool
    @State private var city = "São Paulo"
    @State private var query = ""
    @State private var filters = SearchFilters()
    @State private var showFilters = false
    private var cities: [String] { Array(Set(store.properties.map(\.cidade))).sorted() }
    private var results: [Property] {
        store.properties.filter { p in
            p.cidade == city && (!favoritesOnly || store.favorites.contains(p.id))
            && filters.matches(p)
            && (query.isEmpty || "\(p.neighborhood) \(p.tipo) \(p.imobiliaria)".localizedStandardContains(query))
        }.sorted { $0.preco < $1.preco }
    }
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(favoritesOnly ? "Seu próximo lugar." : "Encontre seu lugar.").font(.largeTitle.bold())
                        Text("\(results.count) imóveis em \(city)").foregroundStyle(.secondary)
                        Picker("Cidade", selection: $city) {
                            ForEach(cities, id: \.self) { Text($0).tag($0) }
                        }.pickerStyle(.segmented)
                    }
                    .padding(.top, 8)
                    if results.isEmpty {
                        ContentUnavailableView(favoritesOnly ? "Nenhum favorito" : "Nenhum imóvel", systemImage: "house", description: Text("Ajuste os filtros ou escolha outra cidade."))
                    }
                    LazyVStack(spacing: 14) {
                        ForEach(results) { property in
                            NavigationLink { PropertyDetail(property: property) } label: {
                                PropertyCard(property: property)
                            }.buttonStyle(.plain)
                        }
                    }
                }.padding()
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle(favoritesOnly ? "Favoritos" : "Imóveis")
            .navigationBarTitleDisplayMode(.inline)
            .searchable(text: $query, prompt: "Bairro, tipo ou imobiliária")
            .toolbar { Button { showFilters = true } label: { Label(filters.count == 0 ? "Filtros" : "Filtros (\(filters.count))", systemImage: "slider.horizontal.3") } }
            .refreshable { await store.refresh(baseAddress: apiAddress) }
            .sheet(isPresented: $showFilters) {
                FiltersView(properties: store.properties.filter {
                    $0.cidade == city && (!favoritesOnly || store.favorites.contains($0.id))
                    && (query.isEmpty || "\($0.neighborhood) \($0.tipo) \($0.imobiliaria)".localizedStandardContains(query))
                }, initial: filters) { filters = $0 }
            }
            .onChange(of: city) { _, _ in filters.neighborhoods = [] }
            .onAppear { if !cities.contains(city), let first = cities.first { city = first } }
        }
    }
}

struct SearchFilters: Equatable {
    var neighborhoods: Set<String> = []
    var types: Set<String> = []
    var minPrice = ""
    var maxPrice = ""
    var bedrooms = 0
    var parking = 0
    static func money(_ value: String) -> Double? {
        let value = value.trimmingCharacters(in: .whitespacesAndNewlines)
            .replacingOccurrences(of: "R$", with: "").replacingOccurrences(of: " ", with: "")
            .replacingOccurrences(of: ".", with: "").replacingOccurrences(of: ",", with: ".")
        guard !value.isEmpty, let amount = Double(value), amount.isFinite, amount >= 0 else { return nil }
        return amount
    }
    var error: String? {
        if (!minPrice.isEmpty && Self.money(minPrice) == nil) || (!maxPrice.isEmpty && Self.money(maxPrice) == nil) {
            return "Informe um preço válido, como 450.000 ou 450.000,50."
        }
        if let low = Self.money(minPrice), let high = Self.money(maxPrice), low > high {
            return "O preço máximo deve ser maior ou igual ao mínimo."
        }
        return nil
    }
    var count: Int { [!neighborhoods.isEmpty, !types.isEmpty, !minPrice.isEmpty || !maxPrice.isEmpty, bedrooms > 0, parking > 0].filter { $0 }.count }
    static func type(of property: Property) -> String {
        property.tipo.components(separatedBy: " à ")[0].components(separatedBy: " para ")[0]
            .trimmingCharacters(in: .whitespacesAndNewlines)
    }
    func matches(_ p: Property) -> Bool {
        (neighborhoods.isEmpty || neighborhoods.contains(p.neighborhood))
        && (types.isEmpty || types.contains(Self.type(of: p)))
        && (Self.money(minPrice).map { p.preco >= $0 } ?? true)
        && (Self.money(maxPrice).map { p.preco <= $0 } ?? true)
        && (bedrooms == 0 || (p.quartos.map { $0 >= bedrooms } ?? false))
        && (parking == 0 || (p.vagas.map { $0 >= parking } ?? false))
    }
}

struct FiltersView: View {
    @Environment(\.dismiss) private var dismiss
    let properties: [Property]
    let apply: (SearchFilters) -> Void
    @State private var draft: SearchFilters
    @FocusState private var priceFocused: Bool
    init(properties: [Property], initial: SearchFilters, apply: @escaping (SearchFilters) -> Void) {
        self.properties = properties
        self.apply = apply
        _draft = State(initialValue: initial)
    }
    private var neighborhoods: [String] { Array(Set(properties.map(\.neighborhood))).sorted() }
    private var types: [String] { Array(Set(properties.map { SearchFilters.type(of: $0) })).sorted() }
    private var total: Int { properties.filter { draft.matches($0) }.count }
    var body: some View {
        NavigationStack {
            Form {
                Section("Localização") {
                    NavigationLink {
                        FilterSelection(title: "Bairros", options: neighborhoods, selection: $draft.neighborhoods)
                    } label: {
                        LabeledContent("Bairros", value: draft.neighborhoods.isEmpty ? "Todos" : "\(draft.neighborhoods.count) selecionados")
                    }
                }
                Section("Tipo de imóvel") {
                    NavigationLink {
                        FilterSelection(title: "Tipos de imóvel", options: types, selection: $draft.types)
                    } label: {
                        LabeledContent("Tipos", value: draft.types.isEmpty ? "Todos" : draft.types.sorted().joined(separator: ", "))
                    }
                }
                Section {
                    HStack {
                        Text("De R$").foregroundStyle(.secondary)
                        TextField("Sem mínimo", text: $draft.minPrice).keyboardType(.decimalPad).focused($priceFocused)
                    }
                    HStack {
                        Text("Até R$").foregroundStyle(.secondary)
                        TextField("Sem máximo", text: $draft.maxPrice).keyboardType(.decimalPad).focused($priceFocused)
                    }
                    if let error = draft.error { Text(error).font(.footnote).foregroundStyle(.red) }
                } header: { Text("Preço de compra") } footer: { Text("Deixe em branco para não limitar o preço.") }
                Section("Características") {
                    Text("Quartos (mínimo)").font(.subheadline)
                    Picker("Quartos", selection: $draft.bedrooms) {
                        Text("Todos").tag(0)
                        ForEach(1...5, id: \.self) { Text("\($0)+").tag($0) }
                    }.pickerStyle(.segmented)
                    Text("Vagas (mínimo)").font(.subheadline)
                    Picker("Vagas", selection: $draft.parking) {
                        Text("Todos").tag(0)
                        ForEach(1...3, id: \.self) { Text("\($0)+").tag($0) }
                    }.pickerStyle(.segmented)
                }
            }
            .navigationTitle("Filtros")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Cancelar") { dismiss() } }
                ToolbarItem(placement: .topBarTrailing) { Button("Limpar") { draft = SearchFilters() } }
                ToolbarItemGroup(placement: .keyboard) { Spacer(); Button("OK") { priceFocused = false } }
            }
            .safeAreaInset(edge: .bottom) {
                Button {
                    priceFocused = false
                    apply(draft)
                    dismiss()
                } label: {
                    Text(total == 0 ? "Nenhum imóvel com esses filtros" : "Ver \(total) imóveis")
                        .font(.headline).frame(maxWidth: .infinity).padding(.vertical, 15)
                }.buttonStyle(.borderedProminent).disabled(draft.error != nil || total == 0)
                    .padding().background(.bar)
            }
        }
    }
}

struct FilterSelection: View {
    let title: String
    let options: [String]
    @Binding var selection: Set<String>
    @State private var query = ""
    var body: some View {
        List {
            Button("Todos") { selection = [] }
            ForEach(options.filter { query.isEmpty || $0.localizedStandardContains(query) }, id: \.self) { option in
                Button {
                    if selection.contains(option) { selection.remove(option) } else { selection.insert(option) }
                } label: {
                    HStack {
                        Text(option).foregroundStyle(.primary)
                        Spacer()
                        if selection.contains(option) { Image(systemName: "checkmark.circle.fill").foregroundStyle(.tint) }
                    }.contentShape(Rectangle())
                }
            }
        }.navigationTitle(title).searchable(text: $query, prompt: "Buscar")
    }
}

struct PropertyCard: View {
    @EnvironmentObject var store: CatalogStore
    let property: Property
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Label(property.tipo, systemImage: "building.2").font(.subheadline).foregroundStyle(.secondary)
                Spacer()
                Image(systemName: store.favorites.contains(property.id) ? "heart.fill" : "chevron.right").foregroundStyle(.tint)
            }
            Text(property.price).font(.title2.bold())
            Text(property.neighborhood).font(.headline)
            HStack(spacing: 18) {
                Label(property.areaLabel, systemImage: "square.dashed")
                if let rooms = property.quartos { Label("\(rooms)", systemImage: "bed.double") }
                if let parking = property.vagas { Label("\(parking)", systemImage: "car") }
            }.font(.caption).foregroundStyle(.secondary)
            Text(property.imobiliaria.replacingOccurrences(of: "_", with: " ")).font(.caption).foregroundStyle(.secondary)
        }.padding(20).frame(maxWidth: .infinity, alignment: .leading)
            .background(.background, in: RoundedRectangle(cornerRadius: 20))
    }
}

struct PropertyDetail: View {
    @EnvironmentObject var store: CatalogStore
    let property: Property
    var body: some View {
        List {
            Section {
                Text(property.price).font(.largeTitle.bold())
                Text("\(property.neighborhood), \(property.cidade) · \(property.uf)")
            }
            Section("Características") {
                LabeledContent("Tipo", value: property.tipo)
                LabeledContent("Área", value: property.areaLabel)
                LabeledContent("Quartos", value: property.quartos.map(String.init) ?? "Não informado")
                LabeledContent("Banheiros", value: property.banheiros.map(String.init) ?? "Não informado")
                LabeledContent("Vagas", value: property.vagas.map(String.init) ?? "Não informado")
                LabeledContent("Fonte", value: property.imobiliaria)
            }
            Section {
                Button { store.toggle(property) } label: {
                    Label(store.favorites.contains(property.id) ? "Remover dos favoritos" : "Salvar nos favoritos", systemImage: "heart")
                }
                if let url = property.safeURL {
                    Link(destination: url) { Label("Abrir anúncio original", systemImage: "arrow.up.right.square") }
                    ShareLink(item: url)
                }
            } footer: { Text("Preço e disponibilidade devem ser confirmados no anúncio original.") }
        }.navigationTitle(property.tipo).navigationBarTitleDisplayMode(.inline)
    }
}

struct SettingsView: View {
    @EnvironmentObject var store: CatalogStore
    @AppStorage("apiAddress") private var apiAddress = "http://localhost:8000"
    var body: some View {
        NavigationStack {
            Form {
                Section("Catálogo offline") {
                    LabeledContent("Imóveis", value: String(store.properties.count))
                    LabeledContent("Atualização", value: String(store.lastUpdate.prefix(10)))
                    Text("O catálogo incluído funciona sem servidor. Favoritos ficam neste aparelho.").font(.footnote).foregroundStyle(.secondary)
                }
                Section("Servidor local (opcional)") {
                    TextField("Endereço da API", text: $apiAddress).keyboardType(.URL).textInputAutocapitalization(.never).autocorrectionDisabled()
                    Button { Task { await store.refresh(baseAddress: apiAddress) } } label: {
                        if store.loading { ProgressView() } else { Text("Atualizar catálogo") }
                    }.disabled(store.loading)
                }
                if let message = store.message { Section { Text(message) } }
            }.navigationTitle("Ajustes")
        }
    }
}
