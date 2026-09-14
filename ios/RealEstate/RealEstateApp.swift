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
    @State private var bedrooms = 0
    @State private var maxPrice = 0.0
    @State private var showFilters = false
    private var cities: [String] { Array(Set(store.properties.map(\.cidade))).sorted() }
    private var results: [Property] {
        store.properties.filter { p in
            p.cidade == city && (!favoritesOnly || store.favorites.contains(p.id))
            && (p.quartos ?? 0) >= bedrooms && (maxPrice == 0 || p.preco <= maxPrice)
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
            .toolbar { Button { showFilters = true } label: { Label("Filtros", systemImage: "slider.horizontal.3") } }
            .refreshable { await store.refresh(baseAddress: apiAddress) }
            .sheet(isPresented: $showFilters) {
                NavigationStack {
                    Form {
                        Stepper("Pelo menos \(bedrooms) quartos", value: $bedrooms, in: 0...6)
                        TextField("Preço máximo (0 = sem limite)", value: $maxPrice, format: .number).keyboardType(.decimalPad)
                        Button("Limpar filtros") { bedrooms = 0; maxPrice = 0 }
                    }.navigationTitle("Filtros")
                    .toolbar { Button("Concluir") { showFilters = false } }
                }.presentationDetents([.medium])
            }
            .onAppear { if !cities.contains(city), let first = cities.first { city = first } }
        }
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
